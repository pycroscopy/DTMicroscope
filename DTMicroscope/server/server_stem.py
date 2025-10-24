import Pyro5.api

from DTMicroscope.base.dummy_mic import DummyMicroscope
# from microscope.afm import AFMMicroscope
from DTMicroscope.base.stem import STEM

## we can download all the data the moment server starts
# import gdown
# file_id = "1V9YPIRi4OLMBagXxT9s9Se4UJ-8oF3_q"# 
# direct_url = f"https://drive.google.com/uc?id={file_id}"
# gdown.download(direct_url, "test.h5", quiet=False)


def serialize_array(array):
    """
    Deserializes a numpy array to a list
    
    args: data: np.array: numpy array
    returns: list: list, shape, dtype
    """
    array_list = array.tolist()
    dtype = str(array.dtype)
    return array_list, array.shape, dtype




@Pyro5.api.expose
class MicroscopeServer(object):
    """Wrapper class for the microscope object
    
    >>>
    >>>
    """
    
    def initialize_microscope(self, microscope = "dummy"):
        if microscope == "dummy":
            self.microscope = DummyMicroscope()
        
        elif microscope == "STEM":
            self.microscope = STEM()
            
        # elif microscope == "afm":
        #     self.microscope = AFMMicroscope()
         
        pass
    
    def register_data(self, data_source = 'test.h5'):
        """
        Given path to the data, loads the data and registers it with the microscope object
        prints the dataset info which includes the channels, units, etc.
        dataset_info useful for querying the data
        """
        
        self.microscope._load_dataset(data_source)
        self.microscope._parse_dataset()
        dataset_info = self.microscope.get_dataset_info()
        print(dataset_info)
        pass
    
    def get_overview_image(self):
        """Returns a checkerboard image
        
        args: size: tuple: size of the image
        returns: numpy array: image
        """        
        image = self.microscope.get_overview_image()
        return serialize_array(image)
    
    def get_point_data(self, spectrum_image_index, x, y):
        """Returns a point data
        
        args: x: int: x coordinate
              y: int: y coordinate
        returns: numpy array: data
        """        
        data = self.microscope.get_point_data(spectrum_image_index, x, y)
        return serialize_array(data)
    
    def get_spectrum_image(self, spectrum_image_index = "Channel_001"):
        """
        To calculate Errors for active learning experiments(DKL)
        TODO: This is more application oriented so need to think of a better structure
        Args:
            spectrum_image_index: Which index in sidpy dataset is spectrum index
            
        Returns: np.array -> shape is 3 dimensional
        """        
        data = self.microscope.get_spectrum_image(spectrum_image_index)
        return serialize_array(data)
    
    def get_spectrum_image_e_axis(self, spectrum_image_index = "Channel_001"):
        """
        To get scalarizers for active learning experiments(DKL)
        TODO: This is more application oriented so need to think of a better structure
        Args:
            spectrum_image_index (str, optional): _description_. Defaults to "Channel_001".
        """
        data = self.microscope.get_spectrum_image_e_axis(spectrum_image_index)
        return serialize_array(data)

    

def main_server():
    host = "0.0.0.0"
    daemon = Pyro5.api.Daemon( port=9091)   #9092=AFM, 9091 = STEM
    uri = daemon.register(MicroscopeServer, objectId="microscope.server")
    print("Server is ready. Object uri =", uri)
    daemon.requestLoop()

    

if __name__ == '__main__':
    main_server()
    
    