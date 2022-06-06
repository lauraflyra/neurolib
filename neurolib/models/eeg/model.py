import numpy as np

import mne
from mne.datasets import eegbci
from mne.datasets import fetch_fsaverage
import os.path as op

###################

# In a different file or functions or whatever, the user would be able to set up their bem and source space, and then
# those are already given to the class




class EEGModel:

    def __init__(self, params, N, subject="fsaverage", subject_dir = None, trans=None, src=None, bem=None, raw_fname = None):

        self.subject = subject
        # subject should always be a string
        # assert subject is string

        self.subject_dir = subject_dir
        # have supported data file and path

        self.src = src
        # assert src is correct file type
        self.trans = trans  # do we calculate trans if not given?? Or do we use fsaverage trans?
        self.bem = bem
        # assert bem is correct file type

        if self.subject == "fsaverage":
            self.loadSubjectData()

        self.raw_fname = raw_fname #info gives electrodes positions
        #check that raw_fname is in the correct format
        # assert raw_fname is edf file

        if self.raw_fname is None:
            # we use what's in example in mne
            self.raw_fname, = eegbci.load_data(subject=1, runs=[6])
        self.loadRawData()
        pass


    def loadSubjectData(self):

        fs_dir = fetch_fsverage(verbose=True)
        subjects_dir = op.dirname(fs_dir)
        self.trans = "fsaverage"
        if self.src is None:
            self.src = op.join(fs_dir, 'bem', 'fsaverage-ico-5-src.fif')
        if self.bem is None:
            self.bem = op.join(fs_dir, 'bem', 'fsaverage-5120-5120-5120-bem-sol.fif')



    def loadRawData(self):
        raw = mne.io.read_raw_edf(self.raw_fname, preload=True)

        # Clean channel names to be able to use a standard 1005 montage
        new_names = dict(
            (ch_name,
             ch_name.rstrip('.').upper().replace('Z', 'z').replace('FP', 'Fp'))
            for ch_name in raw.ch_names)
        raw.rename_channels(new_names)

        # Read and set the EEG electrode locations, which are already in fsaverage's
        # space (MNI space) for standard_1020:
        montage = mne.channels.make_standard_montage('standard_1005')
        raw.set_montage(montage)
        raw.set_eeg_reference(projection=True)  # needed for inverse modeling

    def set_src(self):
        pass

    def set_bem(self):
        pass

    def run(self,  activity, append):
        #this is supposed to do the matrix multiplication leadfield @ activity
        #check wether we downsample here or not, ask Martin and Maria about downsampling
        #maybe this doesnt make sense, maybe calculate leadfields here and not before???

        #check if self.subject == fsaverage
        #else:
        #    self.loadSubjectData

        if self.src is None:
            self.src = make_source() # do we put them in this class or in separate file??

        if self.bem is None:
            self.bem = make_bem() # do we put them in this class or in separate file??


        leadfield = mne.make_forward_model()


        result = leadfield @ activity
        return result








    pass


#IN MODELS/statsmodels.compat.PY

from ..models import eeg

class Model:

    def __init__(self):
        self.eegInitialized = False

    def initializeEEG(self, trans=None, src=None, bem=None):
        # WHY IS self.boldInitialized = False in the beggining of this function????

        #????????????????????????????????????? Where is this attribute created??
        self.eegModel = eeg.EEGModel(self.params, trans,src,bem)
        self.eegInitialized = True

        pass

    def simulateEEG(self, t, variables, append):

        #here we need to check how many nodes we have in the whole brain model, model.params.N == ???
        #because this influences the sources and leadfield and transformation


        if self.EEGInitialized:
            #bla bla

            self.eegModel.run(activity)

        pass

    def run(self,
        bold = False,
        eeg = False,
        ....):

        #here model.EEGModel should already be initialized somewhere!!

        pass