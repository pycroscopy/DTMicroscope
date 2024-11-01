from .microscope import logger
from .microscope import BaseMicroscope
import numpy as np

class DummyMicroscope(BaseMicroscope):
    """
    Testing on server side
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.name = 'Dummy Microscope'
        self.instrument_vendor = 'Dummy'
        self.data_source = 'None'
        self.instrument_type = 'Dummy'
        self.log = []
        # self._log_file_name = 'dummy_microscope_log'
     
    #@logger   
    def get_overview_image(self, size = (128,128)):
        """Returns a checkerboard image
        
        args: size: tuple: size of the image
        returns: numpy array: image
        """
        
        # get a checkerboard image
        image = np.zeros(size)
        image[::2,::2] = 1
        image[1::2,1::2] = 1
        
        return image
    
    #@logger
    def get_point_data(self, x, y):
        """Returns a point data
        
        args: x: int: x coordinate
              y: int: y coordinate
        returns: numpy array: data
        """
        
        return np.array([x,y])
    
    # def get_grid
    
    
    
if __name__ == '__main__':
    dm = DummyMicroscope()
    print(dm.get_overview_image(size = (10,10)))
    print(dm.get_point_data(1,2))
    print(dm.log)
    print(dm.instrument_vendor)
    print(dm.instrument_type)
    print(dm.data_source)
    print(dm.name)