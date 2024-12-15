from DTMicroscope.base.microscope import BaseMicroscope
import SciFiReaders
import pyTEMlib
from pyTEMlib import probe_tools

import pdb
import gdown
import os
import sidpy as sid
from skimage.draw import disk
from random import randint
import random

from ase import build 

# General packages
import os, time, sys, math, io
import matplotlib.pyplot as plt
import numpy as np
import scipy

from skimage.draw import random_shapes
from ase import build 
from scipy.ndimage import gaussian_filter

# The DTSTEM and RealSTEM classes should be interchangeable in the notebooks
class DTSTEM(BaseMicroscope):
    def __init__(self, data_mode):
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
        
    # Initialization functions ---------------------------------------------------------------------------------------------
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


    # Callable functions ---------------------------------------------------------------------------------------------------
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

            # atomic resolution HAADF image ----------------------------------------------------------------------------
            # right now this works for ~10<fov<200
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


            # Blob HAADF image -----------------------------------------------------------------------------------------
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



class RealSTEM():
    def __init__(self):
        print("This implementation cannot be included - the ThermoFisher code is not open source")
        print("If your implementation with DTMicroscope wins a prize, we will take care of the integration to the real microscope")
        print("Thank you!")



