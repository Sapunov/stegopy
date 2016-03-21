#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Methods for working with BMP images."""

from itertools import product
from PIL import Image
import os

_TAG = "gh$_ik3#"


def insert_watermark(imagename, wmname, newimagename):
    """
    Insert watermark in last significant bits of image.

    :param imagename: image for watermarking
    :param wmname: path to the watermark image
    :param newimagename: path to the new image generated
    """
    if not os.path.exists(imagename):
        return ("Error", "File {0} not found".format(imagename))

    if not os.path.exists(wmname):
        return ("Error", "File {0} not found".format(wmname))

    wm = _watermark2bin(wmname)
    wm_len = len(wm)

    image = Image.open(imagename)
    pixels = image.load()
    x, y = image.size
    availible_size = x * y / 8

    if wm_len > availible_size:
        return ("Error", "It's needed {0} bits but only {1} present.".format(
                wm_len, availible_size))

    indexes = product(range(x), range(y))
    mse = 0.0
    snr = 0.0

    for m in wm:
        i = next(indexes)
        blue = pixels[i][2]
        lbit = bin(blue)[-1]

        if "0" == m:
            if "1" == lbit:
                blue -= 1
        elif "1" == m:
            if "0" == lbit:
                blue += 1

        mse += (int(lbit) - int(bin(blue)[-1]))**2
        try:
            snr += int(lbit) ** 2 / (int(lbit) - int(bin(blue)[-1])) ** 2
        except ZeroDivisionError:
            snr += int(lbit) ** 2

        pixels[i] = (pixels[i][0], pixels[i][1], blue)

    image.save(newimagename)

    return (round(mse / availible_size, 4), round(snr, 4))


def extract_watermark(imagename, wmname):
    """
    Extract watermark if exists.

    If watermark exists function extracts one from
    the last significant bits of the specific image.

    :param imagename: filename of the image from here
        we want to extract watermark.
    :param wmname: extracted watermark filename
    """
    if not os.path.exists(imagename):
        raise OSError("File {0} not found".format(imagename))

    image = Image.open(imagename)
    x, y = image.size
    indexes = product(range(x), range(y))
    binvector = []
    tag = _convert2binstr(_TAG)
    tag_len = len(tag)
    tmp = ""
    byte = ""
    switch = False

    for i in range(x * y):
        blue = image.getpixel(next(indexes))[2]
        lbit = bin(blue)[-1]

        if switch:
            tmp = tmp[1:tag_len] + lbit
            byte += lbit
            if 8 == len(byte):
                binvector.append(byte)
                byte = ""
        else:
            tmp += lbit

        if switch:
            if tmp == tag:
                binvector = binvector[:-tag_len / 8]
                break
        else:
            if tmp == tag:
                switch = True

    decvector = [int(j, 2) for j in binvector]

    return _create_grayscale(decvector, wmname)


def calculate_capacity(imagename):
    """Calculation of the maximum size of embedded message."""
    if not os.path.exists(imagename):
        raise OSError("File {0} not found".format(imagename))

    image = Image.open(imagename)
    x, y = image.size

    return x * y / 8


def watermark_len(wmname):
    """How many bits is a watermark size."""
    wm = Image.open(wmname)
    x, y = wm.size

    return x * y * 8


def _create_grayscale(vector, filename):
    """Create grayskale image from vector."""
    x = y = int(len(vector) ** 0.5)
    image = Image.new("L", (x, y))
    image.putdata(vector)

    return image.save(filename)


def _watermark2bin(wmname):
    """Convert watermakr to vector."""
    vm = Image.open(wmname)
    x, y = vm.size
    indexes = product(range(x), range(y))
    vector = []

    for z in range(x * y):
        i, j = next(indexes)
        vector.append(vm.getpixel((j, i)))

    vector = _insert_tags(vector, _TAG)

    return _convert2binstr(vector)


def _convert2binstr(li):
    """Convert string or list of integers to string like '0001010001'."""
    if isinstance(li, basestring):
        return "".join("{0:08b}".format(ord(i)) for i in li)
    elif isinstance(li, list):
        return "".join("{0:08b}".format(i) for i in li)


def _insert_tags(conteiner, tag):
    """Insert special tag on both sides of the container."""
    if not isinstance(conteiner, list):
        return conteiner
    else:
        dec_tag = [ord(i) for i in tag]

        return dec_tag + conteiner + dec_tag
