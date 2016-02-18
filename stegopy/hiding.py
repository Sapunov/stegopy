#!/usr/bin/env python
# -*- coding: utf8 -*-

from PIL import Image
from itertools import product
import os, sys


def hide_message(message, filename, outfile):
    mess = bin_message(message)

    image = Image.open(filename)
    pix = image.load()
    sizex, sizey = image.size

    calculate_capacity(sizex, sizey, len(mess))

    indexes = product(range(sizex), range(sizey))

    for m in mess:
        index = next(indexes)
        b = pix[index][2]

        lastbit = bin(b)[-1]
        if m == '0':
            if lastbit == '1':
                b -= 1
        elif m == '1':
            if lastbit == '0':
                b += 1

        if len(pix[index]) > 3:
            pix[index] = (pix[index][0], pix[index][1], b, pix[index][3])
        else:
            pix[index] = (pix[index][0], pix[index][1], b)

    image.save(outfile)


def calculate_capacity(x, y, msglen):
    cap = x*y/8/1024
    msgsize = msglen/8/1024

    print "Useful capacity of container is", str(cap), "KB"
    print "Message size is", str(msgsize), "KB"

    if msgsize > cap:
        sys.exit(0)



def bin_message(filename):
    with open(filename, "r") as textfile:
        binary = [format(ord(i), 'b') for i in textfile.read()]

    return "".join(binary)
