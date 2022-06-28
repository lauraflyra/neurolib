import nibabel
import numba
import numpy as np


# TODO: the function has to perform well enough to do checks for 1000-10000 dipoles.
def get_labels_of_points(points, atlas="aal2"):
    """ Gives labels of regions the points fall into.
        :points : ndarray of points defined in MNI space (mm).
        :return : (was a label found, label-code, label-string)
        :rtype: (bool, int, str)
    """
    # load
    if atlas == "aal2":
        atlas_img = nibabel.load("./datasets/aal/aal2.nii.gz")
        atlas_labels = None
    else:
        raise

    # get voxel codes
    atlas_img.get_fdata()

    return


@numba.njit()
def get_backprojection(point, atlas_img):
    """ Transform MNI-mm-point into voxel-number.
        :point : 3d point in MNI-coordinate space (mm)
    """
    # Remark: This function assumes continuous (no gaps) definition of the atlas.

    affine_inverse = np.linalg.inv(atlas_img.affine)

    point_expanded = np.hstack((point, 1))
    back_proj = affine_inverse @ point_expanded    # project the point from mni to voxel

    # round to voxel resolution
    back_proj_rounded = np.round(np.diag(affine_inverse) * back_proj, 0) * np.diag(atlas_img.affine)

    return back_proj_rounded
