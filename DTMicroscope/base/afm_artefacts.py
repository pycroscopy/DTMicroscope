"""
author Yu Liu (https://github.com/RichardLiuCoding)
integration into the DT Boris Slautin

"""

import numpy as np
from numba import jit, prange

def real_tip(**kwargs): #TODO how to align it with the real dataset?
    '''
    Nessesary kwargs 'r_tip',
    '''
    if 'r_tip' in kwargs:
        r_tip = kwargs['r_tip']
    else:
        r_tip = 0.05
    if 'scan_size' in kwargs:
        scan_size = kwargs['scan_size']
    if 'center' in kwargs:
        center = kwargs['center']
    else:
        center = np.array([.5, .5])

    X,Y = np.meshgrid(np.linspace(0,1,25), np.linspace(0,1,25))
    center = center
    w = 2*r_tip
    gaussian1 = np.exp(-((X - center[0]) ** 2 / (2 * w ** 2) + (Y - center[1]) ** 2 / (2 * w ** 2)))
    return gaussian1

def tip_doubling(**kwargs):
    pass

@jit(nopython=True, parallel=True)
def pad_image(image, pad_height, pad_width):
    '''
    Pad the image with -1 on the four edges to make sure we can run the kernel through all the pixels.
    Inputs:
        image:    -ndarray: 2D image array to be simulated based on
        pad_height -int: kernel_height // 2
        pad_width  -int:  kernel_width // 2
    Outputs:
        padded_image -ndarray: 2D image array with edge extented by padding -1
    '''
    image_height, image_width = image.shape
    padded_height = image_height + 2 * pad_height
    padded_width = image_width + 2 * pad_width
    padded_image = -np.ones((padded_height, padded_width))  # Use constant value -1 for padding

    for i in prange(image_height):
        for j in prange(image_width):
            padded_image[i + pad_height, j + pad_width] = image[i, j]

    return padded_image
@jit(nopython=True, parallel=True)
def scanning(image, kernel):
    '''
    Scanning image simulated with real probe shapes defined by the kernel.
    '''
    # image = norm_(image)
    image_height, image_width = image.shape
    kernel_height, kernel_width = kernel.shape

    pad_height = kernel_height // 2
    pad_width = kernel_width // 2

    norm_image = (image - np.min(image)) / np.ptp(image)

    padded_image = pad_image(norm_image, pad_height, pad_width)

    output = np.zeros((image_height, image_width))

    for i in prange(image_height):
        for j in prange(image_width):
            crop = padded_image[i:i + kernel_height, j:j + kernel_width]
            output[i, j] = 1 - np.min(2 - kernel - crop)

    return output*np.ptp(image) + np.min(image)




def real_PID():
    pass




