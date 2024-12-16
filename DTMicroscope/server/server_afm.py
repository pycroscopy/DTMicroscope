import numpy as np
import Pyro5.api

# from DTMicroscope.base.dummy_mic import DummyMicroscope
# from microscope.afm import AFMMicroscope
# from DTMicroscope.base.stem import STEM
from DTMicroscope.base.afm import AFM_Microscope
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

# def format_dict(self, data, indent=0):
#     """
#     Recursively format the contents of the dictionary with indented formatting
#     and return it as a string.
#     """
#     result = []
#     spacing = "  " * indent

#     if isinstance(data, dict):
#         for key, value in data.items():
#             result.append(f"{spacing}{key}:")
#             result.append(self.format_dict(value, indent + 1))
#     elif isinstance(data, sidpy.Dataset):
#         result.append(f"{spacing}sidpy.Dataset of type {data.data_type}")
#         result.append(f"{spacing}  data: {data.data}")
#         result.append(f"{spacing}  dimensions:")
#         for dim in data.dimensions:
#             result.append(f"{spacing}    {dim.name}: {dim.values}")
#     else:
#         result.append(f"{spacing}{data}")
    
#     return "\n".join(result)


@Pyro5.api.expose
class MicroscopeServer(object):
    """Wrapper class for the microscope object
    
    >>>
    >>>
    """
    
    def initialize_microscope(self, microscope = "dummy", data_path = r"../test/datasets/dset_spm1.h5"):
        # intialize the class
        if microscope == "dummy":
            self.microscope = DummyMicroscope()
        
        elif microscope == "STEM":
            self.microscope = STEM()
            
        elif microscope == "AFM":
            self.microscope = AFM_Microscope(data_path = data_path)
        print(f"Type of microscope initialized-{microscope}")
        pass
    
    def setup_microscope(self, data_source = 'Compound_Dataset_1', dset_subset = None):
        """
        Parmas:
            datasource : string
        
        Returns: None
        """
        self.microscope.setup_microscope(data_source=data_source, dset_subset = dset_subset)
        
    # def data_dict(self):
    #     """
    #     Params:
    #         None
    #     Returns:
    #         string
        
    #     """
    #     return self.process_and_return_dict(self.microscope.data_dict)
    # def process_and_return_dict(self, data_dict):
    #     """
    #     Params:
    #         data_dict : sidpy_dataset
    #     Returns:
    #         string
    #     """
    #     info_string = format_dict(data_dict)
    #     return info_string


        
    def get_dataset_info(self):
        """
        Params:
            None
        
        Reutns:
            data_info_list : list
        """
        data_info_list = self.microscope.get_dataset_info()
        return data_info_list
    
    # def x(self):
    #     """
    #     Params:
    #         None
    #     Returns:
    #         x : float
    #     """
    #     x = self.microscope.x
    #     print("x is", x)
    #     return x
    
    
    # def y(self):
    #     """
    #     Params:
    #         None
    #     Returns:
    #         y : float
    #     """
    #     y = self.microscope.y
    #     return y
    @property
    def scan_rate(self):
        value = self.microscope.scan_rate
        return value

    @property
    def sample_rate(self):
        value = self.microscope.sample_rate
        return value

    @property
    def x(self):
        value = self.microscope.x
        return value
    
    @property
    def y(self):
        value = self.microscope.y
        return value
    
    
    @property
    def x_min(self):
        """
        Params :
            None
        
        Reutrns :
            x_min : float
        
        """
        return self.microscope.x_min
    
    @property
    def x_max(self):
        """
        Params:
            None
        
        Returns:
            x_max : float
        """
        value = self.microscope.x_max
        return value
    
    @property
    def y_min(self):
        """
        Params :
            None
        
        Reutrns :
            x_min : float
        
        """
        return self.microscope.y_min

    @property
    def y_max(self):
        """
        Params :
            None
        
        Reutrns :
            x_min : float
        
        """
        return self.microscope.y_max
    
    #def get_scan(self, channels = ['HeightRetrace','image_dataset_1'], mod_string = None, mod_kwargs = None):
    def get_scan(self, channels = None, modification=None, scan_rate = None, direction='horizontal', trace='forward'):
        """
        Gets the scan by incorporating appropriate modification
        Prams:
            channels : list
            mod_string : string : options are None, "real_tip", "tip_doubling" , "real_PID"
            mod_kwargs : dict 
                        >>> mod_kwargs : kwargs = {'r_tip': [0.1, 0.05], 'center': [[0.2, 0.5], [0.6, 0.55]], 'length_coef': [1, 0.8]}
                        >>> mod_kwargs = {'I': 2, 'dz':10e-9, 'sample_rate': 2000} # pid
                        >>> mod_kwargs = {'I': 30, 'dz':10e-9, 'sample_rate': 2000} # pid
                        >>> mod_kwargs = {'I': 10, 'dz':10e-9, 'sample_rate': 2000} # pid
        Returns:
            data : numpy array
        """
        # if  mod_string is None:
        #     modification = None
        #     data = self.microscope.get_scan(channels=channels, modification=modification)
        #
        # elif mod_string == "real_tip":
        #     modification = [{'effect': real_tip, 'kwargs': mod_kwargs},]
        #     data = self.microscope.get_scan(channels=channels, modification=modification)
        #
        # elif mod_string == "tip_doubling":
        #     modification = [{'effect': tip_doubling, 'kwargs': mod_kwargs},]
        #     data = self.microscope.get_scan(channels=channels, modification=modification)
        #
        # elif mod_string == "real_PID":
        #     modification = [{'effect': 'real_PID', 'kwargs': mod_kwargs},]
        #     data = self.microscope.get_scan(channels=channels, modification=modification)
        data = self.microscope.get_scan(channels=channels, modification=modification, scan_rate = scan_rate,
                                        direction=direction, trace=trace)

        return serialize_array(data)

    #def scan_individual_line(self, direction = "vertical", coord = -1e-6, channels=['Amplitude1Retrace', 'Phase1Retrace'], mod_string = None, mod_kwargs = None):
    def scan_individual_line(self, direction='horizontal', coord=0, channels=None,
                             modification=None, trace='forward'):
        """
        Params:
            direction : string
            coord : float
            channels : list
            mod_string : string : options are None, "real_tip", "tip_doubling" # pid part add later?
            mod_kwargs : dict
                >>> kwargs = {'r_tip': [0.05, 0.05], 'center': [[0.2, 0.5], [0.6, 0.75]], 'length_coef': [1, 0.9]}

        
        Returns:
            line : array
        
        >>> line = m.scan_individual_line('vertical', coord = -1e-6, channels=['Amplitude1Retrace', 'Phase1Retrace'])
        
        """
        
        # if mod_string == None:
        #     modification = None
        #     line = self.microscope.scan_individual_line(direction=direction, coord=coord, channels=channels, modification=modification)
        #
        # elif mod_string == "real_tip":
        #     modification = [{'effect': real_tip, 'kwargs': mod_kwargs},]
        #     line = self.microscope.scan_individual_line(direction=direction, coord=coord, channels=channels, modification=modification)
        #
        # elif mod_string == "tip_doubling":
        #     modification = [{'effect': tip_doubling, 'kwargs': mod_kwargs},]
        #     line = self.microscope.scan_individual_line(direction=direction, coord=coord, channels=channels, modification=modification)
            
        # elif mod_string == "tip_doubling":
        #     modification = [{'effect': , 'kwargs': mod_kwargs},]
        #     line = self.microscope.scan_individual_line(direction=direction, coord=coord, channels=channels, modification=modification)

        line = self.microscope.scan_individual_line(direction=direction, coord=coord, channels=channels,
                                                    modification=modification, trace=trace)
        return serialize_array(line)
    
    def scanning_emulator(self, scanning_rate=5):
        """
        Params:
            scanning_rate = int
        
        Returns:
            gen : generator --> basically an iterable: no need to serialize this object
            
        >>> gen = m.scanning_emulator(scanning_rate=5)
        >>> line = next(gen)
        """
        gen = self.microscope.scanning_emulator(scan_rate=scanning_rate)
        for line in gen:
            # Convert numpy arrays to lists before yielding them
            yield [l.tolist() for l in line]  # Convert each numpy array to a list
    
    def scan_arbitrary_path(self, path_points = np.array([[-2e-6,2e-6],[1e-6,1.8e-6],[2.1e-6,2e-6]]), channels=['Amplitude1Retrace'], modification=None):
        """
        Params:
            path_points : list -> arrays not allowed
            channels : list
        
        Returns:
            line : array
        """
        path_points = np.array(path_points)
        line = self.microscope.scan_arbitrary_path(path_points=path_points, channels=channels, modification=modification)
        return serialize_array(line)
    
    def get_spectrum(self):
        """
        Params:
            None
        Returns:
                    - _spec_dim (np.ndarray): x_data.
                    - _y (np.ndarray): The spectrum data for the closest point to the given location.
        """
        _spec_dim , _y = self.microscope.get_spectrum()
        return serialize_array(_spec_dim), serialize_array(_y)
    
    def go_to(self, x, y):
        """
        Params:
            x : float/int
            y : float/int
        Returns:
            None
        """
        self.microscope.go_to(x, y)
        return
    

    
def main_server():
    host = "0.0.0.0"
    daemon = Pyro5.api.Daemon( port=9092)  #9092=AFM, 9091 = STEM
    uri = daemon.register(MicroscopeServer, objectId="microscope.server")
    print("Server is ready. Object uri =", uri)
    daemon.requestLoop()

    

if __name__ == '__main__':
    main_server()
    
    
    