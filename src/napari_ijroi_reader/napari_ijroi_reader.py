"""
Main module containing the reader for ImageJ ROI files.
"""
import os
import zipfile

from napari_plugin_engine import napari_hook_implementation

from napari_ijroi_reader.ijroi_utils import decode_roi


def ijroi_read_binary(file_handler):
    """
    Function which reads a single ImageJ ROI.
    The function returns a set of points and a compatible Napari shape type.

    =============  =================
    IJ ROI Type    Napari Shape Type
    =============  =================
    (0)  Polygon   Polygon
    (1)  Rect      Polygon
    (2)  Oval      Polygon
    (3)  Line      Path
    (4)  Freeline  Path
    (5)  Polyline  (Not Supported)
    (6)  NoRoi     (Not Supported)
    (7)  Freehand  Polygon
    (8)  Traced    (Not Supported)
    (9)  Angle     (Not Supported)
    (10) Point     (Not Supported)
    =============  =========

    :param file_handler: A file-like object
    :return: (ShapeType, Points) tuple
    """
    roi_type, points = decode_roi(file_handler)

    shape_type = {
        0: 'polygon',  # polygon
        1: 'polygon',  # rect
        2: 'polygon',  # oval
        3: 'path',  # line
        4: 'path',  # freeline
        5: None,  # polyline
        6: None,  # noRoi
        7: 'polygon',  # freehand
        8: None,  # traced
        9: None,  # angle
        10: None  # point
    }[roi_type]

    if shape_type is None:
        raise ValueError('ROI type %s not supported!' % roi_type)

    return shape_type, points


def ijroi_reader(roi_path):
    """
    Function which reads a single ImageJ ROI file.

    :param roi_path: The path of the ROI file to read
    :return: List of LayerData tuples
    """
    with open(roi_path, 'rb') as file_handler:
        shape_type, points = ijroi_read_binary(file_handler)

    data = [points]
    return [
        (
            data,
            dict(
                name=os.path.basename(roi_path),
                shape_type=shape_type,
                edge_color='red',
                edge_width=1,
                opacity=0.3
            ),
            'shapes'
        )
    ]


def ijroizip_reader(zip_path):
    """
    Function which reads multiple ImageJ ROIs from a ZIP file.

    :param roi_path: The path of the ZIP file to read
    :return: List of LayerData tuples
    """
    shape_types = []
    data = []
    with zipfile.ZipFile(zip_path) as zip_file:
        for name in zip_file.namelist():
            try:
                shape_type, points = ijroi_read_binary(zip_file.open(name))
            except ValueError:
                # TODO: improve error handling
                # we ignore unsupported roi types
                continue
            shape_types.append(shape_type)
            data.append(points)

    return [
        (
            data,
            dict(
                name=os.path.basename(zip_path),
                shape_type=shape_types,
                edge_color='red',
                edge_width=1,
                opacity=0.3
            ),
            'shapes'
        )
    ]


@napari_hook_implementation
def napari_get_reader(path):
    """
    Hock implementation for the Napari plugin.
    The function returns a reader for ImageJ ROI files.

    .. note::

        This hook does not support a list of paths

    :param path: The path of the ImageJ ROI file to read
    :return: The reader or None
    """
    if isinstance(path, str) and path.endswith(".roi"):
        return ijroi_reader
    if isinstance(path, str) and path.endswith(".zip"):
        return ijroizip_reader
    return None
