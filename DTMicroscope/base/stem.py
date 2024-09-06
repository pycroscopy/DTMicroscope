from DTMicroscope.base.microscope import BaseMicroscope
import SciFiReaders
import numpy as np

import pdb
import gdown
import os

# Extracted file ID from the provided URL


class STEM(BaseMicroscope):
    def __init__(self):
        super().__init__()
        self.name = 'STEM Microscope'
        self.instrument_vendor = 'generic'
        self.instrument_type = 'STEM'
        self.data_source = 'None'  # enable people to provide it, generate it or use pre-acquired existing data
        

    def setup_microscope(self, data_source = 'test.h5'):
        ###e.g., generate the data if required at this step
        reader = SciFiReaders.NSIDReader(data_source)
        self.datasets = reader.read()
        return

    def get_overview_image(self, index_of_image = 0):
        return np.array(self.datasets[index_of_image])
        #return np.array(self.datasets[0])
        

    def get_spectrum_image(self, index_of_SI = 1):
        return np.array(self.datasets[index_of_SI])
    
    def get_point_data(self, spectrum_image_index, x, y):
        """emulates the data acquisition at a specific point

        Args:
            spectrum_image_index: Which index in sidpy dataset is spectrum index
            x : position in x
            y : position in y

        Returns:
            numpy array: data at that
            
        >>>spectrum = mic.datasets([1][0][0])
        >>>spectrum  is of shape 1496
        """
        return np.array(self.datasets[spectrum_image_index][x][y])
    
    def pixel_size(self):
        return 0.1
    
    def get_acceleration_voltage(self):
        return 200
        
    
    
    
    # add get spectrum at specific location
    
if __name__== "__main__":
    mic = STEM()
    mic.setup_microscope("/Users/utkarshpratiush/project/DTMicroscope/DTMicroscope/server/test.h5")
    print(mic.get_overview_image())
    pdb.set_trace()
    os.remove("test.h5")
    