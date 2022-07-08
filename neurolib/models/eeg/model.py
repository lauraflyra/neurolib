import numpy as np
import mne
import loadDefaultParams as dp
from neurolib.utils.collections import dotdict
import os
import logging


class EEGModel:

    def __init__(self, params):
        """
        sfreq refers to the sample rate of the data using when creating the info file with the montage
        """

        self.params_eeg = dotdict({})
        self.params_eeg.eeg_conductances = params.get("eeg_conductances")
        # self.params_eeg.eeg_type_scr = params.get("eeg_type_scr")  # volumetric sources are not allowed
        # self.params_eeg.eeg_scr_pos = params.get("eeg_scr_pos")   # volumetric sources are not allowed
        self.params_eeg.eeg_scr_spacing = params.get("eeg_scr_spacing")
        self.params_eeg.eeg_montage_sfreq = params.get("eeg_montage_sfreq")


        self.forward_solution = None

        self.subject_dir = None
        self.subject = None
        self.trans = None
        self.bem = None
        self.eeg_type_src = None
        self.src = None
        self.kind = None
        self.info = None

        if all(value is None for value in self.params_eeg.values()):
            dp.loadDefaultParams(self.params_eeg)
            self.get_precomputed_solution()

        else:
            dp.loadDefaultParams(self.params_eeg)
            self.initialize_solution()

        # TODO: somewhere compare N with the number of regions in the atlas. Assert they are the same

        self.N = params.get("N")  # this is number of nodes
        self.dt = params.get("dt")  # dt of input activity in ms

        self.samplingRate_NDt = int(round(1 / (self.params_eeg.eeg_montage_sfreq * (self.dt / 1000))))
        self.idxLastT = 0  # Index of the last computed t
        self.EEG = np.array([], dtype="f", ndmin=2)
        self.t_EEG = np.array([], dtype="f", ndmin=1)


    def get_precomputed_solution(self):
        logging.warning('This simulation is going to run with the default values and pre-computed forward solution, '
                        'based on a surface source space for fsaverage brain')

        fwd_file = os.path.join(os.path.dirname(__file__), "../..", "data", "datasets", "eeg_fsaverage",
                                "fsaverage_fwd_sol",
                                "fsaverage_surface_src_fixed_orientation-fwd.fif")
        self.forward_solution = mne.read_forward_solution(fwd_file)

    def initialize_solution(self):
        """
        In case the user changes some of the parameters, we need to make a solution, instead of loading the precomputed one

        """
        self.subject_dir = os.path.join(os.path.dirname(__file__), "../..", "data", "datasets", "eeg_fsaverage")
        self.subject = 'fsaverage'
        self.trans = 'fsaverage'

        self.bem = self.set_bem()
        self.eeg_type_src = "surface"
        self.src = self.set_src()
        if self.src is None:
            self.get_precomputed_solution()

        self.kind = "standard_1020"
        montage = mne.channels.make_standard_montage(self.kind, head_size='auto')
        self.info = mne.create_info(ch_names=montage.ch_names, sfreq=self.params_eeg.eeg_montage_sfreq, ch_types='eeg')
        self.info.set_montage(montage)

    def set_bem(self):
        model = mne.make_bem_model(self.subject, ico=4, conductivity=self.params_eeg.eeg_conductances,
                                   subjects_dir=self.subject_dir)
        bem = mne.make_bem_solution(model)
        return bem

    def set_src(self):
        # TODO: catch for type being something wrong
        type = self.eeg_type_src # if we want the source type to be in params_eeg, change this to self.params_egg.eeg_type_src
        if type == 'surface':
            src = mne.setup_source_space(self.subject, subjects_dir=self.subject_dir, spacing=self.params_eeg.eeg_scr_spacing,
                                         add_dist="patch")

        # elif type == 'volumetric':
        #     src = mne.setup_volume_source_space(subject=self.subject, bem=self.bem, pos=self.params_eeg.eeg_scr_pos,
        #                                         subjects_dir=self.subject_dir,
        #                                         add_interpolator=False)

        else:
            logging.warning("This source type is not supported.")
            src = None

        return src

    def downsampling_dummy(self, leadfield):
        # TODO: GO MARTIN
        # output size = self.N
        test = np.ones((leadfield.shape[0], self.N))
        return test

    def run(self, activity, append=False):
        # append is when the simulation was already run before and we want to continue to run it

        # this is supposed to do the matrix multiplication leadfield @ activity
        # check wether we downsample here or not, ask Martin and Maria about downsampling
        # maybe this doesnt make sense, maybe calculate leadfields here and not before???

        if self.forward_solution is None:
            self.forward_solution = mne.make_forward_solution(self.info, trans=self.trans, src=self.src, bem=self.bem,
                                                              meg=False, eeg=True, mindist=0.0)

        leadfield = self.forward_solution['sol']['data']

        # somewhere here should be the downsampling function
        downsampled = self.downsampling_dummy(leadfield)
        # print(downsampled.shape)
        # TODO:which type of activity are we expecting here? Firing rates?
        # we need to think about units, it's in mV, conductivities also have units.
        # activity should probably be in Hz, not kHz as in aln.
        # Hopf has no units
        # Try first with aln, and figure out the correct scale. Then figure out other models without units.

        EEG_output = downsampled @ activity

        # TODO: check with Laura

        # downsample to EEG rate
        EEG_resampled = EEG_output[
                        :, self.samplingRate_NDt - np.mod(self.idxLastT - 1,
                                                          self.samplingRate_NDt)::self.samplingRate_NDt]
        t_new_idx = self.idxLastT + np.arange(activity.shape[1])
        t_EEG_resampled = (
                t_new_idx[self.samplingRate_NDt - np.mod(self.idxLastT - 1,
                                                         self.samplingRate_NDt):: self.samplingRate_NDt]
                * self.dt
        )

        if self.EEG.shape[1] == 0:
            # add new data
            self.t_EEG = t_EEG_resampled
            self.EEG = EEG_resampled
        elif append is True:
            # append new data to old data
            self.t_EEG = np.hstack((self.t_EEG, t_EEG_resampled))
            self.EEG = np.hstack((self.EEG, EEG_resampled))
        else:
            # overwrite old data
            self.t_EEG = t_EEG_resampled
            self.EEG = EEG_resampled

        self.idxLastT = self.idxLastT + activity.shape[1]

        return

    pass
