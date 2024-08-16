"""
Base microscope class

This should be the base class from which all the other microscopes are built from

"""

class BaseMicroscope(object):

    def __init__(self) -> None:
        self.name = 'Base Microscope'
        self.instrument_vendor = 'generic'
        self.data_source = 'None' #enable people to provide it, generate it or use pre-acquired existing data
        self.instrument_type = 'generic' #could be STEM, STM, AFM

    def setup_microscope(self):
        ###e.g., generate the data if required at this step
        return
    
    def scan_raster(self,**args):
        pass
    
    def set_probe_position(self, **args):
        pass
    
    def scan_individual_line(self,**args):
        pass
            
    def scan_arbitary_path(self,**args):
        pass
    
    def get_point_data(self,x,y,**args):
        pass

    def get_grid_data(self,grid_parms, **args):
        pass

    