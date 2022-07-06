import logging
import numpy as np
import numba


def downsample_leadfield_matrix(leadfield: np.ndarray,
                                label_codes: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
        :param leadfield :
        :param label_codes :
        :return :
    """

    unique_labels = np.unique(label_codes)
    unique_labels = np.delete(unique_labels, np.where(np.isnan(unique_labels))[0])  # delete NAN if present
    unique_labels = np.delete(unique_labels, np.where(unique_labels == 0)[0])  # delete 0 if present

    for label in unique_labels:
        if label == 0 or np.isnan(label):
            continue    # invalid or CSF regions are not of interest
        else:
            indices_label = np.where(label_codes == label)[0]

            indiced_label_x = indices_label*3       # x-components
            indiced_label_y = indices_label*3 + 1   # y-components
            indiced_label_z = indices_label*3 + 2   # z-components
            leadfield[:, ]

    logging.info("")

    return None
