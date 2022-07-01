import unittest
from ni_eeg_forward_project.util import access_atlases
import numpy as np


class TestAccessAtlases(unittest.TestCase):

    def test_get_labels_of_points_aal2(self):

        # An arbitrary testing point is the MNI-coordinate (-6, 14, 0). E.g. mentioned in doi:10.1093/brain/awt329
        # that the left caudate nucleus is located there.
        test_point = np.array([[-6, 14, 0]])    # one sample point with known label
        labels = access_atlases.get_labels_of_points(test_point, atlas="aal2")

        expected_result = ([True], np.array([7001, ]), ["Caudate_L"])
        self.assertTupleEqual(expected_result, labels)

