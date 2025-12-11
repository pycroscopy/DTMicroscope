import numpy as np

from DTMicroscope.base.microscope import *
from DTMicroscope.base.afm_artefacts import *

import sidpy as sd
import time
class AFM_Microscope(BaseMicroscope):
    """
    A class representing an Atomic Force Microscope (AFM) used for simulating data generation
    and scanning by AFM. This class provides methods for setting up the microscope,
    scanning the surface, and retrieving data in a simulated environment.

    Attributes:
        name (str): The name of the microscope (default is 'AFM Microscope').
        instrument_vendor (str): The vendor of the instrument (default is 'generic').
        instrument_type (str): The type of the instrument (set to 'AFM').
        data_source (str): The source of the data. It can either be 'generate' for synthetic data
                           generation or a path to an external dataset.
        dataset (dict): The dataset containing scan data (generated or loaded).
        probe_position (tuple): The current (x, y) position of the probe within the scanning grid.
        stage_position (tuple): The global stage position, controlled by piezoelectric motors.
        x_coords (numpy.ndarray): The x-coordinates of the scan grid.
        y_coords (numpy.ndarray): The y-coordinates of the scan grid.
        x (float): The current x-coordinate of the probe position.
        y (float): The current y-coordinate of the probe position.
        log (list): A log that records operations performed by the microscope. #TODO
        gen_params (dict): Parameters used for generating synthetic data. #TODO
        scan_ar (numpy.ndarray): The array holding scanned data from image channels.
        _im_ind (dict): A dictionary that holds the indices of image data channels.
        _sp_ind (dict): A dictionary that holds the indices of spectrum data channels.
        _pc_ind (dict): A dictionary that holds the indices of point cloud data channels.

    Methods:
        setup_microscope(data_source='generate', dset_subset=None)
            Initializes the microscope by generating synthetic data or loading an existing dataset.

        _generate_synthetic_data(grid_size, noise_level) #TODO
            Generates synthetic surface height data based on the specified grid size and noise level.

        process_dataset(dset, compound=False, dset_subset=None)
            Parses and processes the dataset to identify and organize image, spectrum, and point cloud data.

        get_dataset_info():
            Returns a summary of the dataset, including the available channels and their signals.

        get_scan(channels=None, modification=None, scan_rate=0.5):
            Retrieves scan data for the specified channels, applying modifications if provided.

        scanning_emulator(direction='horizontal', channels=None):
            Emulates the scanning process along a horizontal or vertical axis, yielding 2D slices
            of scan data step by step.

        go_to(x, y):
            Moves the probe to the specified (x, y) coordinates, clamping them to valid ranges if necessary.

        scan_individual_line(direction='horizontal', coord=0, channels=None, modification=None):
            Scans a single horizontal or vertical line at the specified coordinate in the grid.

        scan_arbitrary_path(path_points, channels=None):
            Scans along an arbitrary path defined by real-world coordinates and returns the corresponding
            scan values.

        get_spectrum(location=None, channel=None):
            Retrieves the spectrum data at a given (x, y) location, selecting the appropriate point cloud channel.

        _find_closest_point(coords, target_point):
            Finds the closest point in a 2D array of coordinates to the target point (x, y).

        _real_to_pixel(coord_ar):
            Converts real-world coordinates to pixel coordinates based on the scanning grid.

        _bresenham_line(x0, y0, x1, y1):
            Uses Bresenham's algorithm to compute the pixel coordinates along a straight line between two points.
    """

    def __init__(self, data_path = None):
        super().__init__(data_path =data_path)
        self.name = 'AFM Microscope'
        self.instrument_vendor = 'generic'
        self.instrument_type = 'AFM'
        self.data_source = None

        #specify data acquisition rate for PI emulation
        self.sample_rate = 2000 #Hz
        self.scan_rate = 0.5

    def setup_microscope(self, data_source=None, dset_subset = None):
        """
        Initializes the microscope setup by either generating synthetic data or loading pre-existing data.

        Parameters:
            data_source (str): Specifies whether to generate new data ('generate') or path to load pre-existing data.
        """
        self.data_source = data_source
        if self.data_source == 'generate':
            pass #TODO
        #elif self.data_source in self.data_dict['Compound_Datasets']:
        #    # Load pre-existing data
        #    self.process_dataset(dset = self.data_dict['Compound_Datasets'][self.data_source], compound = True, dset_subset=dset_subset)
#
#        elif self.data_source in self.data_dict['Single_Datasets']:
            # Load pre-existing data
#            self.process_dataset(dset = self.data_dict['Single_Datasets'][self.data_source])
        else:
            self.process_dataset(dset = self.data_dict)

    def _generate_synthetic_data(self, ):
        dataset = None
        return dataset

    def process_dataset(self, dset, compound = False, dset_subset = None):
        """
        TODO: Need to discuss how to handle the dictionary of dictionary structures we really have...

        Parses the dataset to identify and index different data types (IMAGE, SPECTRUM, POINT_CLOUD),
        and processes the scan data accordingly.
        
        Input:
            - dset: (dict) of sidpy dataset for processing
            - compound: (bool) True if you are providing a compound dataset.
            - dset_subset: (str, optional): if compound = True, then provide the key for the dataset to be used within the compound dset.
                            Will default to the existing spectroscopic dataset if not provided.

        This method creates three dictionaries to store indices for the different types of data:
        - `_im_ind`: stores indices for IMAGE data.
        - `_sp_ind`: stores indices for SPECTRUM data.
        - `_pc_ind`: stores indices for POINT_CLOUD data.

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
        self.dataset = dset
        
        _keys = list(self.dataset.keys())


        #index dict
        self._im_ind, self._sp_ind, self._pc_ind = {}, {}, {}
        self.scan_ar = []

        if compound:
            if dset_subset is None:
                print("compound dataset detected! We will use the spectroscopic dataset to start")
                self.dataset = dset['spectral_dataset_0']
            elif dset_subset not in dset.keys():
                raise ValueError("The provided key {} is not a dataset within the compound dataset, which has the following keys: {}".format(
                    dset_subset, dset.keys()))
            else:
                self.dataset = dset[dset_subset]

        for i, (key, value) in enumerate(self.dataset.items()):
            data_type = value.data_type
            
            # Store indices and data based on the data type
            if data_type == sd.DataType['IMAGE']:
                self.scan_ar.append(value.compute())
                self._im_ind[key] = i#len(self.scan_ar)-1
            elif data_type == sd.DataType['SPECTRUM'] or data_type==sd.DataType['SPECTRAL_IMAGE']:
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

        #write spatial coordinates
        if len(self._im_ind.items())>0:
            first_im_ind = next(iter(self._im_ind))
        elif len(self._pc_ind.items())>0:
            first_im_ind = next(iter(self._pc_ind))
        elif len(self._sp_ind.items())>0:
            first_im_ind = next(iter(self._sp_ind))
        else:
            raise ValueError("The chosen dataset does not have image, spectra or point clouds. Not supported.")
        
                
        try:
            self.x_coords = self.dataset[first_im_ind].x.values
            self.y_coords = self.dataset[first_im_ind].y.values
        except:
            print("You don't have any x and y coordinates! Using defaults")
            self.x_coords = np.linspace(0,1,self.dataset[first_im_ind].shape[0])
            self.y_coords =  np.linspace(0,1,self.dataset[first_im_ind].shape[1])
        

        self._x_min, self._x_max = float(self.x_coords.min()), float(self.x_coords.max())
        self._y_min, self._y_max = float(self.y_coords.min()), float(self.y_coords.max())

        #place tip in the center of scan
        self._x = float(self.x_coords[len(self.x_coords)//2])
        self._y = float(self.y_coords[len(self.y_coords)//2])
        print('finished processing dataset')


    def _index_to_xy(self, flat_index, num_cols):
        """
        Converts a flat index to the corresponding [x, y] indices in a 2D matrix.

        Parameters:
        flat_index (int): The index in the flattened matrix.
        num_cols (int): The number of columns in the matrix.

        Returns:
        tuple: A tuple of (x, y) coordinates corresponding to the flat index.
        """
        x = flat_index // num_cols
        y = flat_index % num_cols
        return (x, y)

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

    def get_scan(self, channels = None, modification=None, scan_rate = None, trace = 'forward', direction='horizontal'):
        """
            Retrieves scan data from the dataset, optionally filtered by specific channels.

            Parameters:
                channels (list, optional): A list of channel names to filter the scan data.
                                           If None, the entire scan array (`scan_ar`) is returned.
                                           Channels can be specified either by their keys in `_im_ind`
                                           or by their corresponding `quantity` in the dataset.

            Returns:
                numpy.ndarray: A numpy array of the filtered scan data for the specified channels.
                               If no channels are provided, the entire scan array is returned.
        """
        # Return all image channels if channels is None
        if channels is None:
            return self.scan_ar

        self.scan_rate = scan_rate if scan_rate is not None else self.scan_rate or 0.5

        # Ensure channels is a list
        if not isinstance(channels, list):
            raise TypeError('channels must be either None or a list of channel names')

        ind_list = []
        _quantity = [self.dataset[k].quantity for k in self._im_ind]

        for ch in channels:
            # Check if the channel exists in _im_ind (by key)
            if ch in self._im_ind:
                ind_list.append(self._im_ind[ch])
            # Check if the channel exists by quantity
            elif ch in _quantity:
                _ind = _quantity.index(ch)
                _ind_from_lst_im = list(self._im_ind.items())[_ind][1]
                ind_list.append(_ind_from_lst_im)
            else:
                print(f'{ch} is not an IMAGE and was excluded from the returning array')

            # Ensure we have at least one valid channel
            if not ind_list:
                raise ValueError('No valid channels were found to return data.')

        # Return the filtered scan data based on the valid indices
        if modification is None:
            _res_scan = self.scan_ar[ind_list]
        elif type(modification) is list:
            _scan = self.scan_ar[ind_list]
            if direction == 'vertical':
                _scan = np.transpose(_scan, (0,2,1))
            if trace == 'backward':
                _scan = _scan[:,::-1]
            _res_scan = self._apply_modification(_scan, modification, coords=None)
        else:
            raise ValueError(r'''Attribute 'modification' should be list of dict''')

        _res_scan = _res_scan if trace == 'forward' else _res_scan[:,::-1]

        return _res_scan if direction == 'horizontal' else np.transpose(_res_scan, (0, 2, 1))

    def scanning_emulator(self, direction='horizontal', channels=None, scan_rate=None,
                          modification=None):
        """
        Emulates a scanning process over the data, either horizontally or vertically, yielding slices of scan data.

        Parameters:
            direction (str, optional): The scanning direction, either 'horizontal' or 'vertical'.
                                       Defaults to 'horizontal'. Determines how the data will be sliced.
            channels (list, optional): A list of channel names to filter the scan data. If None, the entire scan array is used.

        Yields:
            numpy.ndarray: A 2D slice of the scan data for each step of the emulated scan.
        """
        self.scan_rate = scan_rate if scan_rate is not None else self.scan_rate or 0.5

        # Get the scan data from the provided channels
        _ar_data = self.get_scan(channels, scan_rate=scan_rate, modification=modification)

        # Horizontal scanning: iterate over the second axis (axis 1)
        if direction == 'horizontal':
            l = _ar_data.shape[1]
            for i in range(l):
                if scan_rate is not None:
                    time.sleep(1/scan_rate)
                yield _ar_data[:, i, :]

        # Vertical scanning: iterate over the third axis (axis 2)
        elif direction == 'vertical':
            l = _ar_data.shape[2]
            for i in range(l):
                yield _ar_data[:, :, i]

        # If the direction is neither horizontal nor vertical, raise an error
        else:
            raise ValueError("The 'direction' must be either 'horizontal' or 'vertical'.")

        return

    def go_to(self, x, y):
        """
        Moves the scanning tip to the specified coordinates (x, y). If the provided coordinates are
        out of the valid range (defined by `self.x_coords` and `self.y_coords`), a warning is printed,
        and the coordinates are clamped to the closest valid values.

        Parameters:
            x (float): The desired x-coordinate.
            y (float): The desired y-coordinate.
        """
        x = float(x)
        y = float(y)
        # Check x-coordinate
        if x < self.x_coords.min() or x > self.x_coords.max():
            print(f"Warning: x-coordinate {x} is out of range. Clamping to valid range.")
        self._x = max(self.x_coords.min(), min(x, self.x_coords.max()))

        # Check y-coordinate
        if y < self.y_coords.min() or y > self.y_coords.max():
            print(f"Warning: y-coordinate {y} is out of range. Clamping to valid range.")
        self._y = max(self.y_coords.min(), min(y, self.y_coords.max()))
        return True

    def scan_individual_line(self, direction='horizontal', trace = 'forward', coord=0, channels=None,
                             modification=None):
        """
        Extracts a specific line of data from the scan array, either horizontally or vertically,
        based on the given coordinate and direction.

        Parameters:
            direction (str, optional): The direction to scan, either 'horizontal' or 'vertical'.
                                       Defaults to 'horizontal'.
            coord (float): The specific coordinate (in the x or y direction) where the line will be extracted.
            channels (list, optional): A list of channel names to filter the scan data. If None,
                                       the entire scan array is used.

        Returns:
            numpy.ndarray: A 2D slice (channels, line) of the scan data along the specified line.
        """

        _scan_ar = self.get_scan(channels=channels)
        if direction == 'horizontal':
            # Set the target x-coordinate based on the trace direction
            target_x = self.x_coords.min() if trace == 'backward' else self.x_coords.max()
            self.go_to(x=target_x, y=coord)

            # Find the closest y-coordinate index to the specified coordinate
            _ind = np.argmin(np.abs(self.y_coords - coord))

            # Determine the start and end points for the Bresenham line based on the horizontal direction
            start_x, end_x = (0, _scan_ar.shape[2] - 1) if trace == 'forward' else (_scan_ar.shape[2] - 1, 0)
            _coords = self._bresenham_line(start_x, _ind, end_x, _ind)

        elif direction == 'vertical':
            # Set the target y-coordinate based on the trace direction
            target_y = self.y_coords.max() if trace == 'backward' else self.y_coords.min()
            self.go_to(x=coord, y=target_y)

            # Find the closest x-coordinate index to the specified coordinate
            _ind = np.argmin(np.abs(self.x_coords - coord))

            # Determine the start and end points for the Bresenham line based on the trace direction
            start_y, end_y = (0, _scan_ar.shape[1] - 1) if trace == 'forward' else (_scan_ar.shape[1] - 1, 0)
            _coords = self._bresenham_line(_ind, start_y, _ind, end_y)

        else:
            raise ValueError("The 'direction' must be either 'horizontal' or 'vertical'.")

        if modification is None:
            _line_ar = _scan_ar[:, _coords[:,1], _coords[:,0]]
        elif type(modification) is list:
            _line_ar = self._apply_modification(_scan_ar, modification, _coords)
        else:
            raise ValueError(r'''Attribute 'modification' should be list of dict''')

        return _line_ar if trace == 'forward' else _line_ar[:,::-1]

    def scan_arbitrary_path(self, path_points, channels=None, modification=None):
        """
        Scans the data along an arbitrary path defined by real-world coordinates and returns the corresponding
        scan values. Corrects out-of-range coordinates by clamping them to the closest valid points.

        Parameters:
        ----------
        path_points : list or np.ndarray
            A list or numpy array of shape (N, 2) with N points representing (x, y) coordinates along the desired path.
            The path must have at least two points.
        channels : list, optional
            A list of channel names to filter the scan data. If None, all channels are used.

        Returns:
        -------
        np.ndarray
            A 2D numpy array of scan data extracted from the specified path. The output shape will be (channels, len(path)),
            where each row corresponds to the channel values along the path.
        """

        # Validate input path_points
        path_points = np.array(path_points)
        if path_points.ndim != 2 or path_points.shape[1] != 2 or path_points.shape[0] < 2:
            raise ValueError("path_points must have shape (N, 2), where N > 1 is the number of points.")

        # Get the scan array with selected channels
        _scan_ar = self.get_scan(channels=channels)

        # Correct out-of-range coordinates using vectorized clipping
        corrected_path_points = np.clip(path_points, [self._x_min, self._y_min], [self._x_max, self._y_max])

        # Convert corrected real-world coordinates to pixel coordinates
        pixel_coords = self._real_to_pixel(corrected_path_points)

        # Get all pixels along the path using Bresenham's line algorithm
        path_pixel_coords = np.array([self._bresenham_line(*pixel_coords[i], *pixel_coords[i + 1])
                                      for i in range(len(pixel_coords) - 1)], dtype=object)

        # Flatten the list of lists into an array of pixel coordinates
        path_pixel_coords = np.vstack(path_pixel_coords).astype(int)

        # Extract and return the scan data along the calculated path
        if modification is None:
            _res_ar = _scan_ar[:, path_pixel_coords[:, 0], path_pixel_coords[:, 1]]
        elif type(modification) is list:
            _res_ar = self._apply_modification(_scan_ar, modification, path_pixel_coords)
        else:
            raise ValueError(r'''Attribute 'modification' should be list of dict''')
        return _res_ar

    def _apply_modification(self, scan, modification, coords=None):
        if coords is None: #apply to entire scan
            for eff_dict in modification:
                if type(eff_dict) is dict:
                    kwargs = eff_dict['kwargs']

                    if eff_dict['effect'] == "real_tip":
                        res_scan = np.array([scanning(ar, real_tip(**kwargs)) for ar in scan])
                    elif eff_dict['effect'] == "tip_doubling":
                        res_scan = np.array([scanning(ar, tip_doubling(**kwargs)) for ar in scan])
                    elif eff_dict['effect'] == "real_PID":
                        kwargs['scan_rate'] = float(kwargs.get('scan_rate', self.scan_rate))
                        kwargs['sample_rate'] = float(kwargs.get('sample_rate', self.sample_rate))
                        res_scan = np.array([real_PI(ar, **kwargs) for ar in scan])
                    else:
                        raise ValueError(f"The effect {eff_dict['effect']} is not supported. "
                                         f"The supported effects are 'real_tip', 'tip_doubling', 'real_PID'")
                    return res_scan
        else: #apply to trajectory specified by coords
            for eff_dict in modification:
                if type(eff_dict) is dict:
                    kwargs = eff_dict['kwargs']

                    if eff_dict['effect'] == "real_tip":
                        line_ar = np.array([scanning_trajectory(ar, coords, real_tip(**kwargs)) for ar in scan])
                    elif eff_dict['effect'] == "tip_doubling":
                        line_ar = np.array([scanning_trajectory(ar, coords, tip_doubling(**kwargs)) for ar in scan])
                    elif eff_dict['effect'] == "real_PID":
                        kwargs['scan_rate'] = float(kwargs.get('scan_rate', self.scan_rate))
                        kwargs['sample_rate'] = float(kwargs.get('sample_rate', self.sample_rate))
                        line_ar = np.array([real_PI(ar, coords, **kwargs) for ar in scan])
                    else:
                        raise ValueError(f"The effect {eff_dict['effect']} is not supported. "
                                         f"The supported effects are 'real_tip', 'tip_doubling', 'real_PID'")
                    return line_ar

    def get_spectrum(self, location=None, channel=None):
        """
            Retrieves the spectrum data for a given location.

            Parameters:
                location (tuple, optional): A tuple (x, y) specifying the real-world coordinates of the location.
                                            If None, the current location (self.x, self.y) is used.
                channel (str, optional): The name of the point cloud channel to retrieve data from. If None,
                                         the first available point cloud channel is used.

            Returns:
                tuple: A tuple containing:
                    - _spec_dim (np.ndarray): x_data.
                    - _y (np.ndarray): The spectrum data for the closest point to the given location.
        """
         # Use the current (x, y) location if no location is provided
        if location is None:
            location = (self._x, self._y)

        # Check if point cloud data is available
        if len(self._pc_ind)>0:
            # Select the point cloud channel to use
            if channel is None:
                point_cloud = self.dataset[list(self._pc_ind.keys())[0]]  # Default to the first point cloud channel
            elif channel not in self._pc_ind:
                raise ValueError(f'The selected channel "{channel}" is not a point cloud channel.')
            else:
                point_cloud = self.dataset[channel]

            # Find the closest point in the point cloud to the given location
            _point_coords = point_cloud.point_cloud['coordinates']
            _closest_ind = self._find_closest_point(_point_coords, location)

            # Get the spectrum data for the closest point
            _y = point_cloud[_closest_ind].compute()

            # Get the spectral dimension
            _spectral_dim = point_cloud.get_spectral_dims()
            _spec_dim = point_cloud.get_dimension_by_number(_spectral_dim)[0].values

        elif len(self._sp_ind)>0:
            if channel is None:
                spectrum = self.dataset[list(self._sp_ind.keys())[0]]
            elif channel not in self._sp_ind:
                raise ValueError(f'The selected channel "{channel}" is not a spectral image channel.')
            else:
                spectrum = self.dataset[channel]

            # Find the closest point in the point cloud to the given location
            xp, yp = np.meshgrid(self.x_coords, self.y_coords)
            _point_coords = np.array([xp.ravel(),yp.ravel()]).T
            
            _closest_ind = self._find_closest_point(_point_coords, location)
            #convert the index to x,y
            _closest_ind_x, _closest_ind_y = self._index_to_xy(_closest_ind, num_cols = len(self.y_coords))
           
            # Get the spectrum data for the closest point
            _y = spectrum[_closest_ind_x, _closest_ind_y].compute()

            # Get the spectral dimension
            _spectral_dim = spectrum.get_spectral_dims()
            _spec_dim = spectrum.get_dimension_by_number(_spectral_dim)[0].values
            
        else:
            raise ValueError('There is no point cloud or spectral data in the dataset.')

        return (_spec_dim, _y)

    @staticmethod
    def _find_closest_point(coords, target_point):
        """
        Finds the closest point to the target point in a 2D array of coordinates.

        Parameters:
            coords (np.ndarray): A 2D array of shape (n, 2) representing n points with x and y coordinates.
            target_point (tuple): A tuple (x, y) representing the target point.

        Returns:
            index (int): The index of the closest point in the coords array.
        """

        # Calculate the Euclidean distance between the target_point and all points in the coords array
        distances = np.sqrt(np.sum((coords - target_point) ** 2, axis=1))
        index = np.argmin(distances)
        return index

    def _real_to_pixel(self, coord_ar):
        """
        Transforms an array of real-world coordinates to pixel coordinates in a 2D array, using vectorized operations.

        Parameters:
            coord_ar (np.ndarray): A 2D array of shape (N, 2) containing real-world coordinates (x, y) to be transformed.
            x_ar (np.ndarray): A 1D array of real-world x-coordinates for the pixels.
            y_ar (np.ndarray): A 1D array of real-world y-coordinates for the pixels.

        Returns:
            np.ndarray: A 2D array of shape (N, 2) containing pixel coordinates corresponding to the real-world coordinates.
        """
        # Extract x and y real-world coordinates
        x_real = coord_ar[:, 0]
        y_real = coord_ar[:, 1]

        # Find the closest x and y indices using broadcasting and argmin
        x_pixel = np.argmin(np.abs(self.x_coords[:, np.newaxis] - x_real), axis=0)
        y_pixel = np.argmin(np.abs(self.y_coords[:, np.newaxis] - y_real), axis=0)

        # Combine x and y pixel indices into an array
        pixel_coords = np.stack((x_pixel, y_pixel), axis=-1)

        return pixel_coords
    @staticmethod
    def _bresenham_line(x0, y0, x1, y1):
        """
        Bresenham's line algorithm to get the path between two points (x0, y0) and (x1, y1) on a 2D grid.
        Returns the list of coordinates on the path between the two points.
        """
        path = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            path.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return np.array(path)
    
    @property
    def x_min(self):
        return float(self._x_min)

    @property
    def x_max(self):
        return float(self._x_max)

    @property
    def y_min(self):
        return float(self._y_min)

    @property
    def y_max(self):
        return float(self._y_max)
    
    @property
    def y(self):
        return float(self._y)

    @property
    def x(self):
        return float(self._x)
