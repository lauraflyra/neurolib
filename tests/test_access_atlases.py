import unittest
from neurolib.models.eeg.eeg_util import access_atlases
import numpy as np


class TestAccessAtlases(unittest.TestCase):

    def test_get_labels_of_points_aal2(self):

        # An arbitrary testing point is the MNI-coordinate (-6, 14, 0). E.g. mentioned in doi:10.1093/brain/awt329
        # that the left caudate nucleus is located there.
        test_point = np.array([[-6, 14, 0]])    # One sample point with known label.
        result = access_atlases.get_labels_of_points(test_point, atlas="aal2")
        expected_result = ([True], np.array([7001, ]), ["Caudate_L"])
        self.assertTupleEqual(expected_result, result)

        # A point that should be way out of the space covered by any brain-atlas.
        expected_result = ([False], np.array([np.NAN, ]), ["invalid"])
        test_point = np.array([[1000, 0, 0]])
        points_valid, codes, acronyms = access_atlases.get_labels_of_points(test_point, atlas="aal2")
        self.assertEqual(expected_result[0], points_valid)
        assert np.isnan(codes[0])
        self.assertEqual(expected_result[2], acronyms)

    def test_filter_for_regions(self):
        regions = ["abc", "def"]
        labels = ["0", 0, np.NAN, "abc", "abcdef", "ABC"]
        self.assertListEqual(access_atlases.filter_for_regions(labels, regions),
                             [False, False, False, True, False, False])
