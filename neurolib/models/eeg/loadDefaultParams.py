import numpy as np

from ...utils.collections import dotdict

def loadDefaultParams():
    """Load default parameters for the EEG Model

    :return: A dictionary with the default parameters of the model
    :rtype: dict
    """

    params = dotdict({})

    params.subject = 'fsaverage'
    params.subject_dir =
    params.trans = params.subject



    return params
