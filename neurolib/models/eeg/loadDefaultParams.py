import numpy as np
from neurolib.utils.collections import dotdict


# Since the user should only be able to change the conductances, the type of the sources and the pos/spacing
# we only need to have in the loadDefaultParams.py those four values

def loadDefaultParams(params_eeg):
    """Load default parameters for the EEG Model

    :return: A dictionary with the default parameters of the model
    :rtype: dict
    """
    if params_eeg.eeg_conductances is None:
        params_eeg.eeg_conductances = (0.3, 0.006, 0.3)
    # if params_eeg.eeg_type_scr is None:
    #     params_eeg.eeg_type_scr = "volumetric"
    # if params_eeg.eeg_scr_pos is None:  # source positions refers to volumetric
    #     # sources
    #     params_eeg.eeg_scr_pos = 5.0
    if params_eeg.eeg_scr_spacing is None:  # scr spacing refers to surface sources
        params_eeg.eeg_scr_spacing = "oct6"
    if params_eeg.egg_montage_sfreq is None: #sfreq refers to the sample rate of the
        # data using when creating the info file with the montage
        params_eeg.eeg_montage_sfreq = 256
    if params_eeg.eeg_atlas is None:
        params_eeg.eeg_atlas = "aal2_cortical"  # the 80 cortical regions defined in the AAL2 atlas


# TODO: insert in the README the info about what scr_spacing and that the user should always write in the params dictionary following this nomenclature rule
# TODO: insert in README that for now we only use surface
