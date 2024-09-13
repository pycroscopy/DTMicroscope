import numpy as np
import Pyro5.api
import sys

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
        self.microscope.setup_microscope(data_source)
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
    
    
def main_server():
    host = "0.0.0.0"
    daemon = Pyro5.api.Daemon( port=9091)  
    uri = daemon.register(MicroscopeServer, objectId="microscope.server")
    print("Server is ready. Object uri =", uri)
    daemon.requestLoop()

    

if __name__ == '__main__':
    main_server()
    
    