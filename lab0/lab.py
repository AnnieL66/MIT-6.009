#!/usr/bin/env python3

import sys
import math
import base64
import tkinter

from io import BytesIO
from PIL import Image as Image

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
    # iterate over the loop
    for x in range(result['width']):
        for y in range(result['height']):
            # get pixel from image at location x,y
             color = get_pixel(image, x, y)
             # generate new color
             newcolor = func(color)
             # set the new pixel in result at location x,y
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
                    # input pixel's value multiplied by the associated value
                    # in the kernel
                    # get pixel from image at location x-dis+z, y-dis+i * kernel[i][z]
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
            # value of sharpened image =
            # 2 * image at location (x,y) - blurred image at location (x,y)
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
            # c is the root of the sum of squares of corresponding pixels in Ox and Oy
            c = ((get_pixel(Ox, x, y))**2 + (get_pixel(Oy, x, y))**2)**0.5
            set_pixel(result, x, y, c)
    # ensure that the final image is made up of integer pixels in range [0,255]
    round_and_clip_image(result)
    return result

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_image(filename):
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


def save_image(image, filename, mode='PNG'):
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


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    pass
