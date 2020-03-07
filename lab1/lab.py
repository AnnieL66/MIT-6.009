#!/usr/bin/env python3

import sys
import math
import base64
import tkinter

from io import BytesIO
from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!
        
def get_pixel(image, x, y):
    """
    Returns the pixel value in the given position (x, y).
    """
    pixels = image['pixels'][x + image['width']*y]
    return pixels

def get_pixel_outRange(image, x, y):
    """
    Returns the pixel value in the given position (x, y).
    Set it to the nearest pixel if out of range.
    """
    if x > image['width'] -1:
        x = image['width'] -1
    elif x < 0:
        x = 0
    if y > image['height'] -1:
        y = image['height']-1
    elif y < 0:
        y = 0
    return get_pixel(image, x, y)
        
def set_pixel(image, x, y, c):
    """
    Sets the pixel value at position(x, y) as c
    """
    image['pixels'][x+(image['width']*y)] = c

def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': ([0]*len(image['pixels'])),
        }
    """
    Get inverted image pixels
    """
    for x in range(result['width']):
        for y in range(result['height']):
             color = get_pixel(image, x, y)
             newcolor = func(color)
             set_pixel(result, x, y, newcolor)
    return result

def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)

# HELPER FUNCTIONS
    
def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    """
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': ([0]*len(image['pixels'])),
        }
    #distance from center to edge of kernal
    dis = len(kernel)//2
    #iterate over every pixel in image
    for x in range(image['width']):
        for y in range(image['height']):
            cor = 0;
            for i in range(len(kernel)):
                for z in range(len(kernel[i])):
                    cor += get_pixel_outRange(image, x-dis+z, y-dis+i) * kernel[i][z]
            set_pixel(result, x, y, cor)
    return result
    raise NotImplementedError


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for i in range(len(image['pixels'])):
            image['pixels'][i] = int(round(image['pixels'][i]))
            if image['pixels'][i] < 0:
                image['pixels'][i] = 0
            elif image['pixels'][i] > 255:
                image['pixels'][i] = 255

# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    box_blurred = box_blur(n)
    # then compute the correlation of the input image with that kernel
    result = correlate(image, box_blurred)
    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    round_and_clip_image(result)
    return result

def box_blur(n):
    """
    create a representation for the appropriate n-by-n kernel, and return it
    """
    kernel = []
    # generate an n-by-n kernel
    for i in range(n):
        # generate an empty row list
        row = []
        for j in range(n):
            # n-by-n square of dentical values that sum to 1
            row.append(1/n**2)
        kernel.append(row)
    return kernel

def sharpened(i, n):
    """
    Returns a new image, the result of an "unsharp mask" on self.
    n is the size of box blur kernel
    """
    result = {
        'height': i['height'],
        'width': i['width'],
        'pixels': ([0]*len(i['pixels'])),
        }
    # generate the blurred copy of the image
    blurred = correlate(i, box_blur(n))
    # iterate over loop and use blurred image do calculation
    for x in range(i['width']):
        for y in range(i['height']):
            c = 2 * get_pixel(i, x, y)-get_pixel(blurred, x, y)
            set_pixel(result, x, y, c)
    # ensure that the final image is made up of integer pixels in range [0,255]
    round_and_clip_image(result)
    return result

def edges(im):
    result = {
        'height': im['height'],
        'width': im['width'],
        'pixels': ([0]*len(im['pixels'])),
    }
    # Initialize two kernels: Kx and Ky
    Kx = [[-1, 0, 1],
          [-2, 0, 2],
          [-1, 0, 1]]
    Ky = [[-1, -2, -1],
          [0, 0, 0],
          [1, 2, 1]]
    # computing Ox and Oy by correlating the input with Kx and Ky respectively
    Ox = correlate(im, Kx)
    Oy = correlate(im, Ky)
    # loop over pixels
    for x in range(im['width']):
        for y in range(im['height']):
            # do calculations
            c = ((get_pixel(Ox, x, y))**2 + (get_pixel(Oy, x, y))**2)**0.5
            set_pixel(result, x, y, c)
    # ensure that the final image is made up of integer pixels in range [0,255]
    round_and_clip_image(result)
    return result

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()

# VARIOUS FILTERS
def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color_filter(im):
        red, green, blue = spilt_color(im)
        result = combine_image(filt(red), filt(green), filt(blue))
        return result
    return color_filter

def copy(im):
        """
        Return a new instance of Image with identical size and pixels to this
        image.
        """
        result = {
            'height': im['height'],
            'width': im['width'],
            'pixels': [0]*len(im['pixels']),
            }
        return result

def spilt_color(im):
    """
    Split the given color image into its three components: Red, Green, Blue
    """
    red = copy(im)
    green = copy(im)
    blue = copy(im)
    # iterate over loop
    for x in range(im['width']):
        for y in range(im['height']):
            set_pixel(red, x, y, get_pixel(im, x, y)[0])
            set_pixel(green, x, y, get_pixel(im, x, y)[1])
            set_pixel(blue, x, y, get_pixel(im, x, y)[2])
    return red, green, blue

def combine_image(red, green, blue):
    """
    Re-combine the three components into one single color image
    """
    result = {
        'height': red['height'],
        'width': red['width'],
        'pixels': []
        }
    for y in range(red['height']):
        for x in range(red['width']):
            result['pixels'].append((get_pixel(red, x, y), get_pixel(green, x, y),
                                    get_pixel(blue, x, y)))
    return result
            
def make_blur_filter(n):
    def blur(im):
        return blurred(im, n)
    return blur

def make_sharpen_filter(n):
    def sharpen(im):
        return sharpened(im, n)
    return sharpen
    raise NotImplementedError


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def filter(im):
        result = im
        n = len(filters)
        for i in range(n):
            result = filters[i](result)
        return result
    return filter


# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    for i in range(ncols):
    # Make a greyscale copy of the current image
        result = greyscale_image_from_color_image(image)
    # calculate energy map by calling the compute_energy function
        energy = compute_energy(result)
    # Compute a "cumulative energy map"
        energy_map = cumulative_energy_map(energy)
    # find minimum energy seam
        min_list = minimum_energy_seam(energy_map)
    # remove the computed path
        image = image_without_seam(image, min_list)
    return image

# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    result = copy(image)
    # iterate every pixels in image and set the pixel in result as greyscale
    for y in range(image['height']):
        for x in range(image['width']):
            set_pixel(result, x, y, round(.299 * get_pixel(image, x, y)[0] +
                                      .587 * get_pixel(image, x, y)[1] +
                                      .114 * get_pixel(image, x, y)[2]))
    return result

def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy function),
    computes a "cumulative energy map" as described in the lab 1 writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    result = copy(energy)
    # For each pixel in the row
    for y in range(energy['height']):
        for x in range(energy['width']):
            # Set this value in the "cumulative energmap" to be:
            # the value of that location in the energy map, added to the
            # minimum of the cumulative energies from the "adjacent" pixels in the row
            # above
            pre_energy = adjacent_pixels(result, x, y)[0]
            c = pre_energy + get_pixel(energy, x, y)
            set_pixel(result, x, y, c)
    return result

def adjacent_pixels(im, x, y):
    """
    return minimum of the cumulative energies from the "adjacent" pixels in the row above
    """
    mini = 256*im['height']
    x1 = 0
    # if pixel is leftmost
    if (x == 0):
        # the pixel only has two adjacent pixels in the row above
        # the one upper and the one upper right
        for i in range(x, x+2):
            if (get_pixel(im, i, y-1) < mini):
                mini = get_pixel(im, i, y-1)
                x1 = i
    # if the pixel is rightmost
    elif (x+1 == im['width']):
        # the pixel only has two adjacent pixels in the row above
        # the one upper and the one upper left
        for i in range(x-1, x+1):
            if (get_pixel(im, i, y-1) < mini):
                mini = get_pixel(im, i, y-1)
                x1 = i
    else:
        for i in range(x-1, x+2):
            if (get_pixel(im, i, y-1) < mini):
                mini = get_pixel(im, i, y-1)
                x1 = i
    return (mini, x1)

def minimum_energy_seam(c):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 1 writeup).
    """
    energy_cols = []
    # Get the x coordinate of minimum pixel in the last row
    x1 = c['pixels'][((c['height']-1)*c['width']):].index(min(c['pixels'][((c['height']-1)*c['width']):]))
    # calculate the index of that pixel
    index = x1 + c['width']*(c['height']-1)
    energy_cols.append(index)
    # iterate over loop, starting from the second last row to the top row
    for y in range(c['height']-2, -1, -1):
        # set x1 to the x coordinate of minimum pixel in that row
        x1 = adjacent_pixels(c, x1, y+1)[1]
        index = x1 + c['width']*y
        energy_cols.append(index)
    energy_cols.reverse()
    # return minimum energy column index
    return energy_cols

def image_without_seam(im, s):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    result = copy(im)
    # generate result as a copy of im
    for y in range(im['height']):
        for x in range(im['width']):
            set_pixel(result, x, y, get_pixel(im, x, y))
    # pop out index from result in the list
    for i in range(len(s)-1, -1, -1):
        result['pixels'].pop(s[i])
    # adjust the width of the im
    result['width']-=1
    return result

def threshold(im, low, high):
    red, green, blue = spilt_color(im)
    red = threshold_Helper(red, low, high)
    green = threshold_Helper(green, low, high)
    blue = threshold_Helper(blue, low, high)
    result = combine_image(red, green, blue)
    return result

def threshold_Helper(im, low, high):
    result = copy(im)
    for y in range(im['height']):
        for x in range(im['width']):
            if(get_pixel(im, x, y) > high):
                set_pixel(result, x, y, 255)
            elif(get_pixel(im, x, y) < low):
                set_pixel(result, x, y, 0)
            else:
                set_pixel(result, x, y, get_pixel(im, x, y))
    return result

# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()

if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    pass
