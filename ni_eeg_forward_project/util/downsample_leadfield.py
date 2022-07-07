import logging
import numpy as np


def downsample_leadfield_matrix(leadfield: np.ndarray,
                                label_codes: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """ Take a leadfield-matrix (that contains three dipoles of perpendicular orientation  for each source position)
        and down sample it to an average across all dipoles that fall into a region (for each dipole orientation).

        :param leadfield :  Channels x Dipoles, the dipoles aranged like (d1_x, d1_y, d1_z, d2_x,...), i.e.
                            the leadfield of three dipoles perpendicular to each other for one source location are
                            stored in three consecutive columns.
        :param label_codes : 1D array of labels assigned to the source locations
        :return :
    """
    leadfield_orig_shape = leadfield.shape
    n_channels = leadfield_orig_shape[0]

    if leadfield_orig_shape[1] % 3 != 0:
        raise ValueError("The lead field matrix does not have the expected number of columns. \n"
                         "Has to be multiple of 3 for xyz-components.")

    unique_labels = np.unique(label_codes)
    unique_labels = np.delete(unique_labels, np.where(np.isnan(unique_labels))[0])  # delete NAN if present
    unique_labels = np.delete(unique_labels, np.where(unique_labels == 0)[0])  # delete 0 if present

    x_components = np.zeros((n_channels, unique_labels.size))
    y_components = np.zeros((n_channels, unique_labels.size))
    z_components = np.zeros((n_channels, unique_labels.size))

    for label_idx, label in enumerate(unique_labels):
        indices_label = np.where(label_codes == label)[0]

        indiced_label_x = indices_label*3       # x-components
        indiced_label_y = indices_label*3 + 1   # y-components
        indiced_label_z = indices_label*3 + 2   # z-components

        x_components[:, label_idx] = np.mean(leadfield[:, indiced_label_x], axis=1)
        y_components[:, label_idx] = np.mean(leadfield[:, indiced_label_y], axis=1)
        z_components[:, label_idx] = np.mean(leadfield[:, indiced_label_z], axis=1)

    # logging.info("")
    return unique_labels, x_components, y_components, z_components
