"""
author Yu Liu (https://github.com/RichardLiuCoding)
integration into the DT Boris Slautin

"""

import numpy as np
from numba import jit, prange
from scipy.signal import resample

def real_tip(**kwargs): #TODO how to align tip radius with the real dataset?
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
    if 'r_tip' in kwargs:
        if type(kwargs['r_tip']) not in [list, np.array]:
            raise TypeError('The r_tip must be list for the tip_doubling artefact')
        r_tip = kwargs['r_tip']

    if 'center' in kwargs:
        center = kwargs['center']
    else:
        center = np.random.rand(len(r_tip), 2)

    if 'length_coef' in kwargs:
        lc = kwargs['length_coef']
    else:
        lc = np.ones(len(r_tip))

    gaus = None
    for i in range(len(r_tip)):
        kwargs = {'r_tip': r_tip[i],
                  'center': center[i],
                  }
        if isinstance(gaus, np.ndarray):
            gaus = gaus + real_tip(**kwargs) * lc[i]
        else:
            gaus = real_tip(**kwargs) * lc[i]

    return gaus / np.sum(lc)

def real_PI(scan, coords=None, **kwargs):
    """
    Applies a Proportional-Integral (PI) controller to a 2D scan array.

    This function emulates the application of a PI controller to each row of a 2D scan matrix, adjusting
    the values based on specified proportional (P) and integral (I) gains, buffer length, and a possible
    baseline offset (dz). The PI control is applied to each row individually, using the `PI_trace` function
    for correction.

    Args:
        scan (array-like): A 2D array representing the scan data, where each row is processed by the PI controller.
        **kwargs:
            P (float, optional): Proportional gain. Default is 0.
            I (float, optional): Integral gain. Default is 10.
            buffer_length (int, optional): The length of the integral memory, i.e., number of past errors stored. Default is 500.
            dz (float, optional): Offset to be subtracted from the scan data to account for baseline shift. Default is 0.

    Returns:
        numpy.ndarray: A 2D array where each row has been processed with the PI controller.

    TODO:
        Implement scan direction emulation.

    Raises:
        ValueError: If `scan` is not a 2D array.
    """
    # Retrieve parameters from kwargs with default values
    I = kwargs.get('I', 10)
    P = kwargs.get('P', 0)
    length = int(kwargs.get('buffer_length', 40))
    dz = float(kwargs.get('dz', 0))
    scan_rate = float(kwargs.get('scan_rate', 0.5))
    sample_rate = float(kwargs.get('sample_rate', 2000))

    # Ensure that the input is a 2D array
    if len(scan.shape) != 2:
        raise ValueError("Input scan must be a 2D array.")

    # Initialize output array with the same shape as the input scan
    if coords is None:
        outp = np.zeros_like(scan).T
        for i, row in enumerate(scan.T):
            row_time = resample_trace(row, scan_rate, sample_rate)
            pi_out = PI_trace(row_time, P, I, length, dz)
            mod_trace = resample_trace(pi_out, scan_rate, len(row) * scan_rate)
            outp[i] = mod_trace
        return outp.T
    else:
        _scan_traj = scan[coords[:,1], coords[:,0]]
        number_of_rows = len(_scan_traj) / len(scan[0])
        row_time = resample_trace(_scan_traj, scan_rate, sample_rate, number_of_rows)
        pi_out = PI_trace(row_time, P, I, length, dz)
        outp = resample_trace(pi_out, scan_rate, len(scan[0]) * scan_rate, number_of_rows)
        return outp


@jit(nopython=True, parallel=True)
def scanning_trajectory(image, coords_ar, kernel):
    kernel_height, kernel_width = kernel.shape

    pad_height = kernel_height // 2
    pad_width = kernel_width // 2

    norm_image = (image - np.min(image)) / np.ptp(image)
    padded_image = pad_image(norm_image, pad_height, pad_width)

    output = np.zeros(len(coords_ar))

    for k in prange(len(coords_ar)):
        j,i = coords_ar[k]
        crop = padded_image[i:i + kernel_height, j:j + kernel_width]
        output[k] = 1 - np.min(2 - kernel - crop)

    return output

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

def resample_trace(array, scan_rate, sample_rate, number_of_rows=1):
    """
    Resamples the input array to match a desired sampling rate.

    This function takes an input 1D array (representing a trace or signal) and resamples it
    to match a specified sampling rate, based on the current scan rate. It uses linear interpolation
    to resample the array to the correct number of points.

    Args:
        array (array-like): The input 1D array representing the signal to be resampled.
        scan_rate (float): The current scan rate at which the array was originally acquired.
        sample_rate (float): The target sample rate to which the array should be resampled.

    Returns:
        numpy.ndarray: The resampled array with the number of points adjusted to match the new sample rate.

    Raises:
        ValueError: If the calculated number of points to resample is not valid.
    """
    # Calculate the number of points needed for resampling
    point_number = number_of_rows * sample_rate / scan_rate

    # Ensure the number of points is a valid integer and resample
    if point_number <= 0:
        raise ValueError("The calculated number of points for resampling must be greater than zero.")

    return resample(array, int(point_number))



def push_to_stack(stack, value):
    """
    Pushes a new value into a stack, shifting all elements to the left and placing the new value at the end.

    Args:
        stack (numpy.ndarray): A 1D numpy array representing the stack.
        value (scalar): The new value to be appended to the stack.

    Returns:
        numpy.ndarray: Updated stack with the new value at the last position.
    """
    stack = np.roll(stack, -1)
    stack[-1] = value
    return stack

def PI_trace(trace, P=0, I=10, length=40, dz=0):
    """
    Applies a Proportional-Integral (PI) controller to a 1D signal trace.

    This function emulate PI controller work. It adjusts the trace values to reduce the difference between
    the observed values and the desired reference, applying proportional (P) and
    integral (I) gains. The controller also considers a potential constant offset (dz) under the surface (tapping mode).

    Args:
        trace (array-like): The input 1D signal to be processed.
        P (float, optional): Proportional gain. Controls the immediate response to errors. Default is 0.
        I (float, optional): Integral gain. Controls the cumulative response to errors over time. Default is 1e-2.
        length (int, optional): The length of the integral memory, i.e., the number of past errors stored. Default is 500.
        dz (float, optional): Offset to be subtracted from the trace to account for baseline shift. Default is 0.

    Returns:
        numpy.ndarray: The output array where PI control has been applied.

    Raises:
        ValueError: If the input `trace` is not a 1D array.
    """
    if len(np.shape(trace)) != 1:
        raise ValueError("Input trace must be a 1D array.")

    output = np.zeros_like(trace)
    output[0] = trace[0]

    # Initialize the integral memory with zeros
    integral = np.zeros(length)

    # Iterate through the trace to apply PI control
    for i in range(len(trace) - 1):
        # Compute the difference (error) between the current output and the trace
        z_diff = output[i] - trace[i] - dz

        # Update the integral memory stack with the current error
        integral = push_to_stack(integral, z_diff)

        # Update the output using the PI control formula
        output[i + 1] = max(
            trace[i + 1],
            #we divide I on 1e4 to make it comparable with real AR coeficient
            output[i] - P * z_diff - I / 1e4 * np.sum(integral)

        )

    return output


