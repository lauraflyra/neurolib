import numpy as np


def downsample_leadfield_matrix(leadfield, label_codes):
    """Take a leadfield-matrix (assumes one dipole for each source position, e.g. the usual case for a surface
    source space with orientation of dipoles set as surface normals) and down sample it to an average across all
    dipoles that fall into a region.

    :param leadfield :      Leadfield matrix. Channels x Dipoles.
    :type leadfield:        np.ndarray
    :param label_codes :    1D array of region-labels assigned to the source locations
    :type label_codes:      np.ndarray
    :return :               First, array that contains the label-codes of any region that at least one dipole was
                            assigned to.
                            Second, array that contains Channels x Regions leadfield matrix. The order of rows
                            (channels) is unchanged compared to the input "leadfield", the columns are sorted
                            according to the "unique_labels" array.
    :rtype:                 tuple[np.ndarray, np.ndarray]
    """
    leadfield_orig_shape = leadfield.shape
    n_channels = leadfield_orig_shape[0]

    if leadfield_orig_shape[1] != label_codes.size:
        raise ValueError(
            "The lead field matrix does not have the expected number of columns. \n"
            "Number of columns differs from labels (equal number dipoles)."
        )

    unique_labels = np.unique(label_codes)
    unique_labels = np.delete(
        unique_labels, np.where(np.isnan(unique_labels))[0]
    )  # Delete NAN if present.
    # NAN would indicate point that
    # doesn't fall into space
    # covered by atlas.
    unique_labels = np.delete(
        unique_labels, np.where(unique_labels == 0)[0]
    )  # Delete 0 if present. "0" in AAL2
    # is non-brain-tissue, eg. CSF.

    downsampled_leadfield = np.zeros((n_channels, unique_labels.size))

    for label_idx, label in enumerate(unique_labels):  # iterate through regions
        indices_label = np.where(label_codes == label)[0]

        downsampled_leadfield[:, label_idx] = np.mean(
            leadfield[:, indices_label], axis=1
        )

    return unique_labels, downsampled_leadfield
