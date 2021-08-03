"""
Unittests for the napari_ijroi_reader.ijroi_utils module.
"""
import io
import numpy as np
import struct
from types import SimpleNamespace

from napari_ijroi_reader.ijroi_utils import encode_roi
from napari_ijroi_reader.ijroi_utils import decode_roi


def test_encode_roi():
    """
    Test for the ijroi_utils.encode_roi() function.
    """
    for roi_type, points in [
        [0, np.array([[0, 10], [0, 5]])],
        [1, np.array([[0, 0], [0, 10], [10, 10], [10, 0]])],
        [2, np.array(
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
        )],
        [3, np.array([[0, 0], [0, 10]])],
        [4, np.array([[0, 0], [0, 10], [10, 20]])],
        [7, np.array([[0, 0], [0, 10], [10, 20]])],
    ]:
        y_coords = points[:,0]
        x_coords = points[:,1]

        n_coords = 0
        top, left, bottom, right = 0, 0, 0, 0
        x1, y1, x2, y2 = 0, 0, 0, 0
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
            y1, y2 = y_coords
            x1, x2 = x_coords
            y_coords = []
            x_coords = []

        with io.BytesIO() as mock_handler:
            encode_roi(roi_type, points, mock_handler)  # add data to the stream
            mock_handler.seek(0)

            print('a')
            assert struct.unpack('>4s', mock_handler.read(4))[0] == b'Iout'
            assert struct.unpack('>h', mock_handler.read(2))[0] == 227
            assert struct.unpack('>c', mock_handler.read(1))[0] == bytes([roi_type])
            mock_handler.read(1)
            assert struct.unpack('>h', mock_handler.read(2))[0] == top
            assert struct.unpack('>h', mock_handler.read(2))[0] == left
            assert struct.unpack('>h', mock_handler.read(2))[0] == bottom
            assert struct.unpack('>h', mock_handler.read(2))[0] == right
            assert struct.unpack('>h', mock_handler.read(2))[0] == n_coords
            assert struct.unpack('>f', mock_handler.read(4))[0] == x1
            assert struct.unpack('>f', mock_handler.read(4))[0] == y1
            assert struct.unpack('>f', mock_handler.read(4))[0] == x2
            assert struct.unpack('>f', mock_handler.read(4))[0] == y2
            mock_handler.read(30)
            assert np.abs(np.sum(
                np.asarray(
                    struct.unpack('>%sh' % n_coords, mock_handler.read(n_coords * 2))
                ) - x_coords
            )) < 0.001
            assert np.abs(np.sum(
                np.asarray(
                    struct.unpack('>%sh' % n_coords, mock_handler.read(n_coords * 2))
                ) - y_coords
            )) < 0.001


def test_decode_roi():
    """
    Test for the ijroi_utils.decode_roi() function.
    """
    for expected_roi_type, expected_points in [
        [0, np.array([[0, 0], [0, 0]])],
        [1, np.array([[0, 0], [0, 10], [10, 10], [10, 0]])],
        [2, np.array(
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
        )],
        [3, np.array([[0, 0], [0, 10]])],
        [4, np.array([[0, 0], [0, 10], [10, 20]])],
        [7, np.array([[0, 0], [0, 10], [10, 20]])],
    ]:
        with io.BytesIO() as mock_handler:
            encode_roi(expected_roi_type, expected_points, mock_handler)  # add data to the stream
            mock_handler.seek(0)
            
            roi_type, points = decode_roi(mock_handler)
            
            assert roi_type == expected_roi_type
            assert np.abs(np.sum(points - expected_points)) < 0.001
