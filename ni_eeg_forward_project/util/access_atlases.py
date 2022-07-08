import nibabel
import numpy as np
import logging
from xml.etree import ElementTree


def create_label_lut(path: str) -> dict:
    """ Create a lookup table that contains "anatomical acronyms" corresponding to the encodings of the regions
        specified by the used anatomical atlas. Adds an empty label for code "0" if not specified otherwise by atlas.

        :param : ToDo: proper variable naming depending of the final implementation.
        :return : Dictionary with keys being the integer codes of regions and the values being
    """

    # Look up the codes ("index") and the names of the regions defined by the atlas.
    tree = ElementTree.parse(path)
    root = tree.getroot()
    label_lut = {}
    for region in root.find("data").findall("label"):
        label_lut[region.find("index").text] = region.find("name").text

    if "0 "not in label_lut.keys():
        label_lut["0"] = ""
    return label_lut


def get_labels_of_points(points: np.ndarray, atlas="aal2") -> tuple[list[bool], np.ndarray, list[str]]:
    """ Gives labels of regions the points fall into.

        :param points : Nx3 ndarray of points defined in MNI space (mm).
        :param atlas :  Specification of the anatomical atlas. Remark: Currently only AAL2 is supported.
        :return :       Tuple. First element is a list of bools, indicating for each point if a valid assignment within
                        the space defined by the atlas was found. Second element array of the assigned label-codes.
                        Third, list of strings of the "anatomical acronyms".

    """
    n_points = points.shape[0]
    label_codes = np.zeros(n_points)    # Remark: or expand points-array by one dimension and fill label-codes in there?
    label_strings = [None] * n_points
    points_found = [None] * n_points

    points_expanded = np.ones((n_points, 4))    # Expand by a column with ones only to allow for transformations
    points_expanded[:, 0:3] = points            # with affines.

    if not points.shape[1] == 3:
        raise ValueError

    # Load atlas (integer encoded volume and string-labels).
    if atlas == "aal2":
        atlas_img = nibabel.load("../../neurolib/data/datasets/aal/atlas/AAL2.nii")
        atlas_labels_lut = create_label_lut("../../neurolib/data/datasets/aal/atlas/AAL2.xml")
    else:
        raise ValueError

    affine = atlas_img.affine               # Transformation from voxel- to mni-space.
    affine_inverse = np.linalg.inv(affine)  # Transformation mni- to "voxel"-space.

    # Get voxel codes
    codes = atlas_img.get_fdata()
    for point_idx, point in enumerate(points_expanded):
        back_proj = get_backprojection(point, affine, affine_inverse)

        try:
            label_codes[point_idx] = codes[int(back_proj[0]), int(back_proj[1]), int(back_proj[2])]

        except IndexError:
            #logging.error("The atlas does not specify an assignment for the given MNI-coordinate.")
            label_codes[point_idx] = np.NAN

        if np.isnan(label_codes[point_idx]):
            points_found[point_idx] = False
            label_strings[point_idx] = "invalid"
        else:
            points_found[point_idx] = True
            label_strings[point_idx] = atlas_labels_lut[str(int(label_codes[point_idx]))]   # ToDo: clean up type-
                                                                                       # conversions.
    if sum(points_found) < n_points:
        logging.error(f"The atlas does not specify valid labels for all the given points.\n"
                      f"Total number of points: (%s) out of which (%s) were validly assigned."
                 % (n_points, sum(points_found)))
    return points_found, label_codes, label_strings


def get_backprojection(point_expanded: np.ndarray, affine, affine_inverse) -> np.ndarray:
    """ Transform MNI-mm-point into voxel-number.

        :param point_expanded : 4x1 array. First elements being the 3d point in MNI-coordinate space (mm),
                                last element being a 1 for the offset in transformations.
        :param affine:          4x4 matrix. Projects voxel-numbers to MNI coordinate space (mm).
        :param affine_inverse:  4x4 matrix. Back projection from MNI space.
        :return :               4x1 array. The point projected back into "voxel-number-space", last element 1.
    """
    # Remark: This function assumes continuous (no gaps) definition of the atlas.

    back_proj = affine_inverse @ point_expanded    # project the point from mni to voxel

    # Round to voxel resolution, multiplication with elements inverse is equivalent to division with elements of the
    # affine here.
    back_proj_rounded = np.round(np.diag(affine_inverse) * back_proj, 0) * np.diag(affine)

    return back_proj_rounded
