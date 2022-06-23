import numpy as np

from ...utils.collections import dotdict


# Since the user should only be able to change the conductances, the type of the sources and the pos/spacing
# we only need to have in the loadDefaultParams.py those four values

def loadDefaultParams(conductances=None, type_scr=None, scr_pos=None, scr_spacing=None):
    """Load default parameters for the EEG Model

    :return: A dictionary with the default parameters of the model
    :rtype: dict
    """

    params = dotdict({})

    if conductances is None:
        params.eeg_conductances = ()  # insert here standard values
    if type_scr is None:
        params.eeg_type_scr = "volumetric"
    if scr_pos is None:  # source positions refers to volumetric sources
        params.eeg_scr_pos = 5.0
    if scr_spacing is None:  # scr spacing refers to surface sources
        params.eeg_scr_spacing = "oct6"

    return params

# TODO: insert in the README the info about what scr_pos and scr_spacing and that the user should always write in the params dictionary following this nomenclature rule
# TODO: insert in README that if scr_spacing is changed, but the scr_type is not, then we are still gonna use volumetric with standard value for it