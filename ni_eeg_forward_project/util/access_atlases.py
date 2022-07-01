import nibabel
import numpy as np
import logging
from xml.dom import minidom


# TODO: the function has to perform well enough to do checks for 1000-10000 dipoles.
def get_labels_of_points(points: np.ndarray, atlas="aal2") -> tuple[list[bool], np.ndarray, list[str]]:
    """ Gives labels of regions the points fall into.
        :points : ndarray of points defined in MNI space (mm).
        :return : (was a label found, label-code, label-string)
        :rtype: (bool, int, str)
    """
    n_points = points.shape[0]
    label_codes = np.zeros(n_points)    # Remark: or expand points-array by one dimension and fill label-codes in there?
    label_strings = [None] * n_points
    points_found = [None] * n_points

    points_expanded = np.ones((n_points, 4))    # expand by a column with ones only to allow for transformations
    points_expanded[:, 0:3] = points            # with affines

    if not points.shape[1] == 3:
        raise ValueError

    # load atlas (integer encoded volume and string-labels)
    if atlas == "aal2":
        atlas_img = nibabel.load("./datasets/aal/atlas/AAL2.nii")
        atlas_labels = None
    else:
        raise

    affine = atlas_img.affine               # transformation from voxel to mni-space
    affine_inverse = np.linalg.inv(affine)  # mni to "voxel" space

    # get voxel codes
    codes = atlas_img.get_fdata()
    for point_idx, point in enumerate(points_expanded):
        back_proj = get_backprojection(point, affine, affine_inverse)

        try:
            label_codes[point_idx] = codes[int(back_proj[0]), int(back_proj[1]), int(back_proj[2])]

        except IndexError:
            logging.error("")
            label_codes[point_idx] = np.NAN

        if np.isnan(label_codes[point_idx]):
            points_found[point_idx] = False
            label_strings[point_idx] = ""
        else:
            points_found[point_idx] = True
            label_strings[point_idx] = "label"

    return points_found, label_codes, label_strings


def get_backprojection(point_expanded: np.ndarray, affine, affine_inverse):
    """ Transform MNI-mm-point into voxel-number.
        :point : 3d point in MNI-coordinate space (mm)
    """
    # Remark: This function assumes continuous (no gaps) definition of the atlas.

    back_proj = affine_inverse @ point_expanded    # project the point from mni to voxel

    # round to voxel resolution
    back_proj_rounded = np.round(np.diag(affine_inverse) * back_proj, 0) * np.diag(affine)

    return back_proj_rounded
