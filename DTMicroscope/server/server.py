import numpy as np
import Pyro5.api
import sys

from DTMicroscope.base.dummy_mic import DummyMicroscope
# from microscope.afm import AFMMicroscope



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
    """
    
    def activate_microscope(self, microscope = "dummy"):
        if microscope == "dummy":
            self.microscope = DummyMicroscope()
            
        # elif microscope == "afm":
        #     self.microscope = AFMMicroscope()
         
        pass
        
    def get_overview_image(self, size = (128,128)):
        """Returns a checkerboard image
        
        args: size: tuple: size of the image
        returns: numpy array: image
        """
        
        image = self.microscope.get_overview_image(size)
        return serialize_array(image)
    
    def get_point_data(self, x, y):
        """Returns a point data
        
        args: x: int: x coordinate
              y: int: y coordinate
        returns: numpy array: data
        """
        
        data = self.microscope.get_point_data(x, y)
        return serialize_array(data)
    
    
def main():
    host = "0.0.0.0"
    daemon = Pyro5.api.Daemon(host=host, port=9091)  
    uri = daemon.register(MicroscopeServer, objectId="microscope.server")
    print("Server is ready. Object uri =", uri)
    daemon.requestLoop()

if __name__ == '__main__':
    main()
    