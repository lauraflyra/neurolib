import unittest
from neurolib.models.eeg.eeg_util.downsample_leadfield import downsample_leadfield_matrix
import numpy as np


class TestDownsampleLeadfield(unittest.TestCase):

    def test_downsample_leadfield_matrix(self):
        test_matrix = np.repeat(np.arange(0, 10, 1), 6).reshape((-1, 6))  # ten channels, six source locations
        test_matrix[:, 1] = -test_matrix[:, 1]      # make dipoles of first region cancel each other out
        test_matrix[:, 2] = test_matrix[:, 2] + 2   #

        label_codes = np.array((0, 1, 2, 3, 1, 2))  # First source is in not-of-interest area, the other five sources
                                                    # fall into three different regions.

        unique_labels, downsampled_leadfield = downsample_leadfield_matrix(test_matrix, label_codes)

        self.assertTrue(np.all(downsampled_leadfield.shape == (10, 3)))

        expected_results = {1: np.zeros(10), 2: np.arange(0, 10, 1)+1, 3: np.arange(0, 10, 1)}

        for idx_label, label in enumerate(unique_labels):
            self.assertTrue(np.all(expected_results[label] == downsampled_leadfield[:, idx_label]))
