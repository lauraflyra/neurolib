import matplotlib.pylab
import numpy as np
import matplotlib.pyplot as plt
from mne.forward import forward


def plot_glassbrain_projections(fwd: forward,
                                label_codes: np.ndarray,
                                region_label: int,
                                region_name: str="") -> plt.figure:
    """
        :param fwd: Forward solution object. The whole brain is assumed to be defined in fwd['src'][0].
        :param label_codes:
        :param region_label:
        :param region_name:

    """
    #ToDo: axes labels in MNI-coordinates

    hem = fwd['src'][0]
    dip_pos = hem['rr'][hem['vertno']]*1e3  # The position of the dipoles.

    indices_region = np.where(label_codes == region_label)[0]

    fig, axs = plt.subplots(3, 1)
    axs[0].plot(dip_pos[:, 0], dip_pos[:, 1], 'o', alpha=0.05)
    axs[0].plot(dip_pos[indices_region, 0], dip_pos[indices_region, 1], 'ro', alpha=0.7)

    axs[1].plot(dip_pos[:, 1], dip_pos[:, 2], 'o', alpha=0.05)
    axs[1].plot(dip_pos[indices_region, 1], dip_pos[indices_region, 2], 'ro', alpha=0.7)

    axs[2].plot(dip_pos[:, 0], dip_pos[:, 2], 'o', alpha=0.05)
    axs[2].plot(dip_pos[indices_region, 0], dip_pos[indices_region, 2], 'ro', alpha=0.7)

    plt.suptitle(region_name)

    return fig
