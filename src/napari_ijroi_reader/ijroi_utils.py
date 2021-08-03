"""
Module containing the ImageJ ROI encoder/decoder.

This module was adapted from the mahotas-imread package (https://github.com/luispedro/imread)
written by Luis Pedro Coelho (<luis@luispedro.org>) and published under the MIT license.

ROI format definition:
ImageJ/NIH Image 64 byte ROI outline header 2 byte numbers are big-endian signed shorts

======  ==============================================================================
OFFSET  DESCRIPTION
======  ==============================================================================
0-3     "Iout"
4-5     version (>=217)
6-7     roi type (encoded as one byte)
8-9     top
10-11   left
12-13   bottom
14-15   right
16-17   NCoordinates
18-33   x1,y1,x2,y2 (straight line) | x,y,width,height (double rect) | size (npoints)
34-35   stroke width (v1.43i or later)
36-39   ShapeRoi size (type must be 1 if this value>0)
40-43   stroke color (v1.43i or later)
44-47   fill color (v1.43i or later)
48-49   subtype (v1.43k or later)
50-51   options (v1.43k or later)
52-52   arrow style or aspect ratio (v1.43p or later)
53-53   arrow head size (v1.43p or later)
54-55   rounded rect arc size (v1.43p or later)
56-59   position
60-63   header2 offset
64-     x-coordinates (short), followed by y-coordinates
======  ==============================================================================

References:
http://rsbweb.nih.gov/ij/developer/source/ij/io/RoiDecoder.java.html
http://rsbweb.nih.gov/ij/developer/source/ij/io/RoiEncoder.java.html
"""
from enum import IntEnum
import struct

from matplotlib.patches import Ellipse
import numpy as np


class Options(IntEnum):
    """
    Option flags for ROIs.
    """
    SPLINE_FIT = 1
    DOUBLE_HEADED = 2
    OUTLINE = 4
    OVERLAY_LABELS = 8
    OVERLAY_NAMES = 16
    OVERLAY_BACKGROUNDS = 32
    OVERLAY_BOLD = 64
    SUB_PIXEL_RESOLUTION = 128
    DRAW_OFFSET = 256


def encode_roi(roi_type, points, file_handler):
    """
    Function which encodes a single ImageJ ROI.
    The following ROI types are supported:

    =====  ===========  =========
    Type   Description  Supported
    =====  ===========  =========
    0      Polygon      Yes
    1      Rect         Yes
    2      Oval         Yes
    3      Line         Yes
    4      Freeline     Yes
    5      Polyline     No
    6      NoRoi        No
    7      Freehand     Yes
    8      Traced       No
    9      Angle        No
    10     Point        No
    =====  ===========  =========

    .. note::

        This function does not support any options.

    :param roi_type: The roi type
    :param points: The xy coordinates
    :param file_handler: A file-like object
    """
    points = np.asarray(points).astype(np.int32)
    y_coords = points[:, 0]
    x_coords = points[:, 1]

    n_coords = 0
    top, left, bottom, right = 0, 0, 0, 0
    x1_coord, y1_coord, x2_coord, y2_coord = 0, 0, 0, 0
    if roi_type in [0, 4, 7]:
        n_coords = len(points)
    elif roi_type == 1:
        top, bottom = np.min(y_coords), np.max(y_coords)
        left, right = np.min(x_coords), np.max(x_coords)
        y_coords = []
        x_coords = []
    elif roi_type == 2:
        bottom, top = np.min(y_coords), np.max(y_coords)
        left, right = np.min(x_coords), np.max(x_coords)
        y_coords = []
        x_coords = []
    elif roi_type == 3:
        y1_coord, y2_coord = y_coords
        x1_coord, x2_coord = x_coords
        y_coords = []
        x_coords = []

    data = struct.pack(
        '>4shcchhhhhffffhiiihhcchii%sh' % (n_coords * 2),
        b'Iout',  # magic number
        227,  # version
        bytes([roi_type]),  # roi type
        b'0',
        top,  # top
        left,  # left
        bottom,  # bottom
        right,  # right
        n_coords,  # NCoordinates
        x1_coord,  # x1 (straight line) | x (double rect) | size (npoints)
        y1_coord,  # y1 (straight line) | y (double rect) | size (npoints)
        x2_coord,  # x2 (straight line) | width (double rect) | size (npoints)
        y2_coord,  # y2 (straight line) | height (double rect) | size (npoints)
        0,  # stroke width
        0,  # ShapeRoi size
        0,  # stroke color
        0,  # fill color
        0,  # subtype
        0,  # options
        bytes([0]),  # arrow style or aspect ratio
        bytes([0]),  # arrow head size
        0,  # rounded rect arc size
        0,  # position
        0,  # header2 offset
        *x_coords,
        *y_coords
    )

    file_handler.write(data)


def decode_roi(file_handler):
    # pylint: disable=R0914,W0612
    """
    Function which decodes a single ImageJ ROI.
    The following ROI types are supported:

    =====  ========  =========
    ID     Type      Supported
    =====  ========  =========
    0      Polygon   Yes
    1      Rect      Yes
    2      Oval      Yes
    3      Line      Yes
    4      Freeline  Yes
    5      Polyline  No
    6      NoRoi     No
    7      Freehand  Yes
    8      Traced    No
    9      Angle     No
    10     Point     No
    =====  ========  =========

    .. note::

        This function only supports the SUB_PIXEL_RESOLUTION option.

    :param file_handler: A file-like object
    :return: (RoiType, Points) tuple
    """
    (
        magic, version, roi_type, _, top, left, bottom, right, n_coords,
        x1_coord, y1_coord, x2_coord, y2_coord,
        stroke_width, shape_roi_size, stroke_color, fill_color, subtype, options,
        arrow_style, arrow_head_size, rect_arc_size, position, header2_offset
    ) = struct.unpack('>4shcchhhhhffffhiiihhcchii', file_handler.read(64))
    roi_type = ord(roi_type)

    if magic != b'Iout':
        raise IOError('Magic number not found')
    if not 0 <= roi_type < 11:
        raise ValueError('roireader: ROI type %s not supported' % roi_type)
    if roi_type not in [0, 1, 2, 3, 4, 7]:
        raise ValueError('roireader: ROI type %s not supported' % roi_type)
    if shape_roi_size > 0:
        raise ValueError(
            'roireader: Shape ROI size {} not supported (!= 0)'.format(shape_roi_size)
        )
    if subtype != 0:
        raise ValueError('roireader: ROI subtype {} not supported (!= 0)'.format(subtype))

    if options & Options.SUB_PIXEL_RESOLUTION:
        cformat = '>%sf' % n_coords
        ctype = np.float32
    else:
        cformat = '>%sh' % n_coords
        ctype = np.int16

    if roi_type in [0, 4, 7]:  # polygon, freeline, freehand
        points = np.empty((n_coords, 2), dtype=ctype)
        points[:, 1] = struct.unpack(cformat, file_handler.read(n_coords * 2))
        points[:, 0] = struct.unpack(cformat, file_handler.read(n_coords * 2))
        points[:, 1] += left
        points[:, 0] += top
    elif roi_type == 1:  # rect
        points = np.empty((4, 2), dtype=ctype)
        points[0, :] = (top, left)
        points[1, :] = (top, right)
        points[2, :] = (bottom, right)
        points[3, :] = (bottom, left)
    elif roi_type == 2:  # oval
        height = bottom - top
        width = right - left
        points = Ellipse(
            (top + (height // 2), left + (width // 2)), height, width
        ).get_verts()
    elif roi_type == 3:  # line
        points = np.empty((2, 2), dtype=ctype)
        points[0, :] = (y1_coord, x1_coord)
        points[1, :] = (y2_coord, x2_coord)

    return (roi_type, points)
