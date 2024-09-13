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

    

    def _parse_dataset(self):
        """
        Parses the dataset to identify and index different data types (IMAGE, SPECTRUM, POINT_CLOUD),
        and processes the scan data accordingly.

        TODO: Add ability to associate individual image datasets with spectroscopic datasets. 
        This will need to be done by adding UIDs for each dataset and associating the spectroscopic dataset to the image
        #in original_metadata, have a key for 'UID' and a key for 'associated-image' (the latter will only be for spectroscopic)
        #or also have 'associated-spec' to refer to associated spectroscopic files
        #When we read through the metadata we can immediately identify the available spectroscopic exps.

        In fact the rest of this function coudl be moved into 'process datasets' to assemble the combined ones...
        

        This method creates three dictionaries to store indices for the different types of data:
        - `_im_ind`: stores indices for IMAGE data.
        - `_sp_ind`: stores indices for SPECTRUM data.
        - `_pc_ind`: stores indices for POINT_CLOUD data.
        - `_si_ind`: stores indices for SPECTRAL_IMAGE data. 

        It compiles the image data into a numpy array (`scan_ar`), extracts spatial coordinates from the first
        image dataset, and places the scanning tip at the center of the scan.

        Attributes:
            self._im_ind (dict): Dictionary mapping IMAGE dataset keys to their respective indices.
            self._sp_ind (dict): Dictionary mapping SPECTRUM dataset keys to their respective indices.
            self._pc_ind (dict): Dictionary mapping POINT_CLOUD dataset keys to their respective indices.
            self.scan_ar (numpy.ndarray): Array of computed image data.
            self.x_coords (numpy.ndarray): Array of x-coordinates for spatial positioning.
            self.y_coords (numpy.ndarray): Array of y-coordinates for spatial positioning.
            self.x (float): x-coordinate of the scanning tip, placed at the center of the scan.
            self.y (float): y-coordinate of the scanning tip, placed at the center of the scan.
        """

        _keys = list(self.dataset.keys())
        #index dict
        self._im_ind, self._sp_ind, self._pc_ind = {}, {}, {}
        self.scan_ar = []

        for i, (key, value) in enumerate(self.dataset.items()):
            data_type = value.data_type

            # Store indices and data based on the data type
            if data_type == sd.DataType['IMAGE']:
                self._im_ind[key] = i
                self.scan_ar.append(value.compute())
            elif data_type == sd.DataType['SPECTRUM']:
                self._sp_ind[key] = i
            elif data_type == sd.DataType['POINT_CLOUD']:
                self._pc_ind[key] = i

        # Convert the collected image data to a numpy array
        if self.scan_ar:
            try:
                self.scan_ar = np.array(self.scan_ar)
            except ValueError as e:
                raise ValueError(
                    "Inconsistent scan data. Ensure all scans have the same dimensions.") from e

        #write spacial coordinates
        first_im_ind = next(iter(self._im_ind))
        self.x_coords = self.dataset[first_im_ind].x.values
        self.y_coords = self.dataset[first_im_ind].y.values

        self.x_min, self.x_max = self.x_coords.min(), self.x_coords.max()
        self.y_min, self.y_max = self.y_coords.min(), self.y_coords.max()

        #place tip in the center of scan
        self.x = self.x_coords[len(self.x_coords)//2]
        self.y = self.y_coords[len(self.y_coords)//2]

    def get_dataset_info(self):
        _keys = self.dataset.keys()
        info_list = [
            ('channels', list(_keys)),
            ('signals', [self.dataset[k].quantity for k in _keys]),
            ('units', [self.dataset[k].units for k in _keys]),
            ('scans', list(self._im_ind.values())),
            ('spectra', list(self._sp_ind.values())),
            ('point_clouds', list(self._pc_ind.values())),
        ]
        return info_list
    
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

    