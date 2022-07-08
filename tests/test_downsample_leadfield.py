import unittest
from ni_eeg_forward_project.util.downsample_leadfield import downsample_leadfield_matrix
import numpy as np


class TestDownsampleLeadfield(unittest.TestCase):

    def test_downsample_leadfield_matrix(self):
        test_matrix = np.repeat(np.arange(0, 10, 1), 6).reshape((-1, 6))    # ten channels, two source locations
        test_matrix[:, 0] = -test_matrix[:, 0]  # make x-components of the two dipoles cancel each other out

        label_codes = np.array((1, 1))  # both sources part of the same region

        unique_labels, x_components, y_components, z_components = downsample_leadfield_matrix(test_matrix, label_codes)

        self.assertEqual(unique_labels[0], 1)
        self.assertTrue(np.all(x_components == 0))
        self.assertTrue(np.all(y_components.flatten() == np.arange(0, 10, 1)))
        self.assertTrue(np.all(z_components.flatten() == np.arange(0, 10, 1)))

        # Edge case: test for not-of-interest regions only.
        label_codes = np.array((0, np.NAN))
        unique_labels, x_components, y_components, z_components = downsample_leadfield_matrix(test_matrix, label_codes)
        self.assertFalse(np.any(unique_labels))     # should come back empty
        self.assertFalse(np.any(x_components))
        self.assertFalse(np.any(y_components))
        self.assertFalse(np.any(z_components))

        # Test for sorting when not-of-interest regions are taken out.
        test_matrix = np.zeros((5, 9))  # five channels, three source locations
        test_matrix[:, 0] = np.ones(5)
        test_matrix[:, 3] = 5*np.ones(5)
        test_matrix[:, 6] = 3*np.ones(5)

        label_codes = np.array((1, 0, 1))
        unique_labels, x_components, y_components, z_components = downsample_leadfield_matrix(test_matrix, label_codes)

        self.assertEqual(unique_labels[0], 1)
        self.assertTrue(np.all(x_components.flatten() == 2))

