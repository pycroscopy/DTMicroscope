"""
Base microscope class

This should be the base class from which all the other microscopes are built from

"""

import inspect

def logger(func):
    """Although the following wrapper should technically work 
    for all sorts of methods (static, class),
    We want to write the log to an attribute of the 'self' object.
    This creates problems for static and class methods,
    since they are not bound to self
    Since we do not have any static or class methods now, 
    we will cross that bridge when we get to it."""
    def wrapper(*args, **kwargs):
        bound_args = inspect.signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()
        all_args = bound_args.arguments
        log_fname = all_args['self']._log_file_name
        all_args.pop('self')._log.append({func.__name__: all_args})
        with open("{}.txt".format(log_fname), "a") as logsave:
            logsave.write("\n\n" + str({func.__name__: all_args}))

        return func(*args, **kwargs)
    return wrapper


class BaseMicroscope(object):

    def __init__(self) -> None:
        self.name = 'Base Microscope'
        self.instrument_vendor = 'generic'
        self.data_source = 'None' #enable people to provide it, generate it or use pre-acquired existing data
        self.instrument_type = 'generic' #could be STEM, STM, AFM
        self.log = []] #microscope should have a log

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

    