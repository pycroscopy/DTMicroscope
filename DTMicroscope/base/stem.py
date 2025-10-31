from DTMicroscope.base.microscope import BaseMicroscope
import SciFiReaders
import pyTEMlib
from pyTEMlib import probe_tools

import sidpy as sid

from ase import build 

# General packages
import matplotlib.pyplot as plt
import numpy as np
import scipy

from skimage.draw import random_shapes

# Extracted file ID from the provided URL

class STEM(BaseMicroscope):
    def __init__(self):
        super().__init__()
        self.name = 'STEM Microscope'
        self.instrument_vendor = 'generic'
        self.instrument_type = 'STEM'
        self.data_source = 'None'  # enable people to provide it, generate it or use pre-acquired existing data
        

    def _load_dataset(self, data_source = 'test.h5'):
        ###e.g., generate the data if required at this step
        reader = SciFiReaders.NSIDReader(data_source)
        self.dataset = reader.read()
        # reader.close()
        try:
            # Attempt to access keys attribute to check if dataset is already a dictionary
            dataset_keys = self.dataset.keys()

        except AttributeError:
            # AttributeError is raised because 'dataset' is a list, so convert it to a dictionary
            dataset_dict = {}
            for i, item in enumerate(self.dataset):
                key = f"Channel_{i:03}"  # Format key with zero-padding, e.g., 'channel_000'
                dataset_dict[key] = item
            self.dataset = dataset_dict
        print("Dataset loaded", self.dataset)
        return None

    def get_overview_image(self, channel_key = "Channel_000"):
        print("channel_key", channel_key)
        return np.array(self.dataset[channel_key])
        #return np.array(self.datasets[0])

    def _parse_dataset(self):
        """
        Parses the dataset to identify and index different data types (IMAGE, SPECTRUM, POINT_CLOUD),
        and processes the scan data accordingly.

        This method creates three dictionaries to store indices for the different types of data:
        - `_im_ind`: stores indices for IMAGE data.
        - `_sp_ind`: stores indices for SPECTRUM data.
        - `_pc_ind`: stores indices for POINT_CLOUD data.
        - `_spi_ind`: stores indices for SPECTRAL_IMAGE data.

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
        self._im_ind, self._sp_ind, self._pc_ind, self._spi_ind = {}, {}, {}, {}
        self.scan_ar = []# scan area?

        for i, (key, value) in enumerate(self.dataset.items()):
            data_type = value.data_type

            # Store indices and data based on the data type
            if data_type == sid.DataType['IMAGE']:
                self._im_ind[key] = i
                self.scan_ar.append(value.compute())
            elif data_type == sid.DataType['SPECTRUM']:
                self._sp_ind[key] = i
            elif data_type == sid.DataType['POINT_CLOUD']:
                self._pc_ind[key] = i
            elif data_type == sid.DataType['SPECTRAL_IMAGE']:
                self._spi_ind[key] = i



    def get_dataset_info(self):
        """
        TODO: add metadata info like: pixel size, accelaration voltage, convergence angle, etc.

        # so user can use this info to query the data
        """
        _keys = self.dataset.keys()
        info_list = [
            ('channel_keys', list(_keys)),
            ('signals', [self.dataset[k].quantity for k in _keys]),
            ('units', [self.dataset[k].units for k in _keys]),
            ('scans_channel_index', list(self._im_ind.values())), # eg: HAADF
            ('spectra_channel_index', list(self._sp_ind.values())), #
            ('point_clouds_channel_index', list(self._pc_ind.values())),
            ('spectral_image_channel_index', list(self._spi_ind.values())), # eg: EELS at each pixel in scan
            ('indexing', "image data['CHannel_000'] top left corner is (0,0)"),
            
        ]
        return info_list
    
    def get_point_data(self, spectrum_image_key, x, y):
        """emulates the data acquisition at a specific point

        Args:
            spectrum_image_key: Which index in sidpy dataset is spectrum index
            x : position in x
            y : position in y

        Returns:
            numpy array: data at that
            
        >>>spectrum = mic.datasets([1][0][0])
        >>>spectrum  is of shape 1496
        """
        return np.array(self.dataset[spectrum_image_key][x][y])
    
    
    def get_spectrum_image(self, spectrum_image_key="Channel_001"):
        """
        We need to calculate Errors for active learning experiments(DKL)
        Args:
            spectrum_image_index: Which index in sidpy dataset is spectrum index
            
        Returns: np.array -> shape is 3 dimensional
        """

        return np.array(self.dataset[spectrum_image_key])
    
    def get_spectrum_image_e_axis(self, spectrum_image_key = "Channel_001"):
        """
        To figure out scalarizers for active learning experiments(DKL). We need the energy range.
        TODO: This is more application oriented so need to think of a better structure
        Args:
            spectrum_image_index (str, optional)
        Returns: np.array
        """
        return self.dataset[spectrum_image_key].dim_2.values
    
        
    def pixel_size_X(self):
        return

    def pixel_size_Y(self):
        return 
    
    def get_acceleration_voltage(self):
        return


# The DTSTEM and smart_proxy classes should be interchangeable in the notebooks
class DTSTEM_proxy(BaseMicroscope):
    def __init__(self, data_mode):
        super().__init__()
        if data_mode.lower() == 'simulation':
            self.data_mode = 'simulation'
        elif data_mode.lower() == 'preloaded':
            self.data_mode = 'preloaded'
        else:
            raise ValueError('Invalid data_mode. Please choose "simulation" or "preloaded"')


        self.microscope_name = 'Spectra300'


        self.optics={'mode': 'STEM', # or TEM in the future'aberrations': None,
                     'accelerating_voltage': 200e3, # V
                     'convergence_angle': 30, # mrad
                     'beam_current': 100, # pA
                     'fov': None,
                     'aberrations' : None,
                     'probe': None,
                     'ronchigram': None}
        
        self.initialize_aberrations()
        self.initialize_probe()
        self.initialize_ronchigram()


        self.detectors={'haadf': {'inserted': False},
                        'maadf': {'inserted': False},
                        'bf': {'inserted': False},
                        'camera': {'inserted': False},
                        'flucamera': {'inserted': False,
                                      'screen_current': None,
                                      'exposure_time': None}}
        
    # Initialization functions 
    def initialize_aberrations(self):
        self.aberrations = probe_tools.get_target_aberrations(self.microscope_name, self.optics['accelerating_voltage'])
        self.aberrations['reciprocal_FOV'] = reciprocal_FOV = 150*1e-3 # warning for these two lines - play heavily into probe calculations and all fft convolutions
        self.fov = 1/self.aberrations['reciprocal_FOV']
        self.aberrations['extent'] = [-reciprocal_FOV*1000,reciprocal_FOV*1000,-reciprocal_FOV*1000,reciprocal_FOV*1000]
        self.aberrations['size'] = 512
        self.aberrations['wavelength'] = probe_tools.get_wavelength(self.optics['accelerating_voltage'])
        return

    def initialize_probe(self, sizeX = 512*2):
        sizeX = sizeX
        probe_FOV  = 20
        # self.aberrations['Cc'] = 1
        # self.aberrations['C10'] = 0

        ronchi_FOV = 350 #mrad
        condensor_aperture_radius =  30  # mrad
        ronchi_condensor_aperture_radius = 30  # mrad
        self.aberrations['FOV'] = probe_FOV
        self.aberrations['convergence_angle'] = condensor_aperture_radius # change to optics - make sure everything still runs
        probe, A_k, chi  = pyTEMlib.probe_tools.get_probe(self.aberrations, sizeX, sizeX,  scale = 'mrad', verbose= True)
        self.optics['probe']= probe
        return

    def initialize_ronchigram(self):
        self.aberrations['ronchigram'] = probe_tools.get_ronchigram(1024, self.aberrations, scale = 'mrad')
        return


    # Callable functions
    def connect(self, ip, port):
        print('Connected to Digital Twin')
        return
    
    def set_field_of_view(self, fov):
        self.optics['fov'] = fov
        return self.optics['fov']

    def get_scanned_image(self, size, dwell_time, detector='haadf', seed = None, angle = 0, atoms = None):
        if self.data_mode == 'preloaded':
            return self.haadf_image

        elif self.data_mode == 'simulation':
            self.initialize_probe()
            self.initialize_ronchigram()
    
            if self.optics['fov'] is None:
                raise ValueError('Field of view not set, run microscope.set_field_of_view()')

            # atomic resolution HAADF image
            # right now this works for ~10<fov<200
            # change this to match pystemsim
            if self.optics['fov'] < 300: # Angstroms
                if atoms is None:
                    # Use Al structure
                    atoms = build.fcc110('Al', size=(2, 2, 1), orthogonal=True)
                    atoms.pbc = True
                    atoms.center()
                intensity = 1000 * dwell_time

                # create potential
                potential = pyTEMlib.image_tools.get_atomic_pseudo_potential(fov=self.optics['fov'], atoms=atoms, size = size, rotation=angle)

                probe, image = pyTEMlib.image_tools.convolve_probe(self.aberrations, potential)
                self.optics['probe'] = probe

                # adding shot noise
                image = image / image.max()
                image *= intensity 
                shot_noise = np.random.poisson(image)
                detector_noise = np.random.poisson(np.ones(image.shape))
                image = shot_noise + detector_noise

                return image


            # Blob HAADF image
            elif self.optics['fov'] > 1000: # Angstroms, arbitrary for now
                number_of_electrons = 100 * dwell_time # approximation here ***** Gerd
                size = 512

                image, _ = random_shapes((size, size), min_shapes=20, max_shapes=35, shape='circle',
                            min_size=size*0.1, max_size = size*0.2, allow_overlap=False, num_channels=1, rng=seed)
                image = 1-np.squeeze(image)/image.max()
                image[image<.1] = 0
                image[image>0] = number_of_electrons
                noise = np.random.poisson(image)
                image = image+noise+np.random.random(image.shape)*noise.max()

                # Multiply by the probe
                image = scipy.signal.fftconvolve(image, self.optics['probe'], mode='same')

                return image

            else:
                raise ValueError('Field of view should be < 300 or > 1000 Angstroms')