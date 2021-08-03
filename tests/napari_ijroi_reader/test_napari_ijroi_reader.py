"""
Unittests for the napari_ijroi_reader.napari_ijroi_reader module.
"""
import io
import numpy as np
import struct
from types import SimpleNamespace

from napari_ijroi_reader.ijroi_utils import encode_roi
from napari_ijroi_reader.napari_ijroi_reader import ijroi_reader
from napari_ijroi_reader.napari_ijroi_reader import ijroizip_reader


def test_ijroi_reader(mocker):
    """
    Test for the napari_ijroi_reader.ijroi_reader() function.
    """
    for in_data, out_data in [
        [[0, np.array([[0, 0], [0, 0]])], ['polygon', ]],
        [[1, np.array([[0, 0], [0, 10], [10, 10], [10, 0]])], ['polygon', ]],
        [[2, np.array(
            [[ 5.        ,  0.        ],
             [ 4.01225483,  0.06585394],
             [ 2.20947317,  0.81259056],
             [ 1.46446609,  1.46446609],
             [ 0.81259056,  2.20947317],
             [ 0.06585394,  4.01225483],
             [ 0.        ,  5.        ],
             [ 0.06585394,  5.98774517],
             [ 0.81259056,  7.79052683],
             [ 1.46446609,  8.53553391],
             [ 2.20947317,  9.18740944],
             [ 4.01225483,  9.93414606],
             [ 5.        , 10.        ],
             [ 5.98774517,  9.93414606],
             [ 7.79052683,  9.18740944],
             [ 8.53553391,  8.53553391],
             [ 9.18740944,  7.79052683],
             [ 9.93414606,  5.98774517],
             [10.        ,  5.        ],
             [ 9.93414606,  4.01225483],
             [ 9.18740944,  2.20947317],
             [ 8.53553391,  1.46446609],
             [ 7.79052683,  0.81259056],
             [ 5.98774517,  0.06585394],
             [ 5.        ,  0.        ]]
        )], ['polygon', ]],
        [[3, np.array([[0, 0], [0, 10]])], ['path', ]],
        [[4, np.array([[0, 0], [0, 10], [10, 20]])], ['path', ]],
        [[7, np.array([[0, 0], [0, 10], [10, 20]])], ['polygon', ]],
    ]:
        roi_type, points = in_data
        shape_type, = out_data

        with io.BytesIO() as mock_handler:
            encode_roi(roi_type, points, mock_handler)  # add data to the stream
            mock_handler.seek(0)

            mocker.patch(
                'builtins.open',
                return_value=mock_handler
            )

            layer_data = ijroi_reader("test.roi")
            assert len(layer_data) == 1
            data, props, _ = layer_data[0]
            assert props['shape_type'] == shape_type
            assert len(data) == 1  # we expect only a single shape
            assert np.abs(np.sum(data[0] - points)) < 0.001


def test_ijroizip_reader(mocker):
    """
    Test for the napari_ijroireader.ijroizip_reader() function.
    """
    class ZipMockFile():
        def __init__(self):
            self._data = {}
        def __enter__(self):
            return self
        def __exit__(self, type, value, traceback):
            for name in self._data:
                self._data[name].close()
        def namelist(self):
            return self._data.keys()
        def add_roi(self, roi_type, points):
            name = str(len(self._data) + 1)
            file_handler = io.BytesIO()
            encode_roi(roi_type, points, file_handler)
            file_handler.seek(0)
            self._data[name] = file_handler
        def open(self, name):
            return self._data[name]

    with ZipMockFile() as mock_zip_handler:
        polygon_points = np.array([[0, 0], [0, 0]])
        rect_points = np.array([[0, 0], [0, 10], [10, 10], [10, 0]])
        mock_zip_handler.add_roi(0, polygon_points)
        mock_zip_handler.add_roi(1, rect_points)

        mocker.patch(
            'zipfile.ZipFile',
            return_value=mock_zip_handler
        )

        layer_data = ijroizip_reader("test.zip")
        assert len(layer_data) == 1
        data, props, _ = layer_data[0]
        assert props['shape_type'] == ['polygon', 'polygon']
        assert len(data) == 2  # we expect two shapes
        for shape_id in range(len(data)):
            if shape_id == 0:
                assert np.abs(np.sum(data[shape_id] - polygon_points)) < 0.001
            elif shape_id == 0:
                assert np.abs(np.sum(data[shape_id] - rect_points)) < 0.001
