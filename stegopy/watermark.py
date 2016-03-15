#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Methods for working with watermarks."""

import qrcode


def generate(text, filename):
    """Generate QRCode png image with such text in filename path."""
    qr = qrcode.QRCode(
        version=None,
        box_size=4,
        border=1
    )

    qr.add_data(text)

    return qr.make_image().save(filename)
