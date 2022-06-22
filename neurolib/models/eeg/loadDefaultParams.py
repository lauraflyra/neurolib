import numpy as np

from ...utils.collections import dotdict


# Since the user should only be able to change the conductances, the type of the sources and the pos/spacing
# we only need to have in the loadDefaultParams.py those three values

def loadDefaultParams():
    """Load default parameters for the EEG Model

    :return: A dictionary with the default parameters of the model
    :rtype: dict
    """

    params = dotdict({})

    params.eeg_conductances = ()
    params.eeg_type_scr = "volumetric"
    params.eeg_scr_pos = 5.0
    params.eeg_scr_spacing = None #default for scr_spacing is None, because scr_spacing is only for surface.

    return params