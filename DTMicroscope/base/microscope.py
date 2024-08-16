"""
Base microscope class

This should be the base class from which all the other microscopes are built from

"""

class BaseMicroscope(object):

    def __init__(self) -> None:
        self.name = 'Base Microscope'
        self.instrument_vendor = 'generic'
        self.data_source = 'None'
        self.instrument_type = 'generic' #could be STEM, STM, AFM

    def scan_raster(**args):
        pass
    
    def scan_individual_line(**args):
        pass
            
    def scan_arbitary_path(**args):
        pass
    
    def perform_point_spectroscopy(x,y,spectroscopy_parms,**args):
        pass

    def perform_grid_spectroscopy(grid_parms, spectroscopy_parms),**args:
        pass

    