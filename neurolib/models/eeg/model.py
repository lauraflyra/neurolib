import numpy as np
import mne
import loadDefaultParams as dp
from neurolib.utils.collections import dotdict
import os


class EEGModel:

    def __init__(self, params):
        """
        sfreq refers to the sample rate of the data using when creating the info file with the montage
        """

        params_eeg = dotdict({})
        params_eeg.eeg_conductances = params.get("eeg_conductances")
        params_eeg.eeg_type_scr = params.get("eeg_type_scr")
        params_eeg.eeg_scr_pos = params.get("eeg_scr_pos")
        params_eeg.eeg_scr_spacing = params.get("eeg_scr_spacing")
        params_eeg.eeg_montage_sfreq = params.get("eeg_montage_sfreq")

        #TODO: check, if the person didn't change any params, we actually create anything new, we just load the fsaverage forward solution
        # check if all values in params_eeg are None
        dp.loadDefaultParams(params_eeg)


        print(params_eeg, params_eeg.keys())

        # TODO: get rid of this and acces trough params_eeg ! or get rid of
        #  params_eeg
        self.conductances = params_eeg.eeg_conductances
        self.type_scr = params_eeg.eeg_type_scr
        self.scr_pos = params_eeg.eeg_scr_pos
        self.scr_spacing = params_eeg.eeg_scr_spacing
        self.sfreq = params_eeg.get('eeg_montage_sfreq')

        self.N = params.get("N")  # this is number of nodes
        self.dt = params.get("dt")  # dt of input activity in ms
        self.samplingRate_NDt = int(round(1/(self.sfreq * (self.dt/1000))))

        self.idxLastT = 0  # Index of the last computed t

        # TODO: somwhere compare N with the number of regions in the atlas. Assert they are the same

        # Since the user should only be able to change the conductances, the type of the sources and the pos/spacing
        # we only need to have in the loadDefaultParams.py those four values.

        # TODO: When the user doesnt change all params accordingly we should give a warning saying it's gonna run with default values
        # TODO: change directories the way that Nicola said

        self.subject_dir = os.path.join(os.path.dirname("eeg_fsaverage"), "..", "data", "datasets", "eeg_fsaverage")
        self.subject = 'fsaverage'
        self.subject_dir = None
        self.trans = 'fsaverage' #TODO: understand what does trans = 'fsaverage' do

        self.bem = self.set_bem()
        self.src = self.set_src()

        # TODO: make our own BEM model, maybe then we can keep the function set_bem
        # TODO: make our own source model, maybe then we can keep the function set_scr

        # TODO: maybe keep default files for src and bem

        self.kind = "standard_1020"
        montage = mne.channels.make_standard_montage(self.kind, head_size='auto')
        self.info = mne.create_info(ch_names=montage.ch_names, sfreq=self.sfreq, ch_types='eeg')
        self.info.set_montage(montage)

        self.EEG = np.array([], dtype="f", ndmin=2)
        self.t_EEG = np.array([], dtype="f", ndmin=1)


    def set_bem(self):
        model = mne.make_bem_model(self.subject, ico = 4, conductivity = self.conductances,
                                   subjects_dir = self.subject_dir)
        bem = mne.make_bem_solution(model)
        return bem

    def set_src(self):
        # TODO: catch for type being something wrong
        type = self.type_scr
        if type == 'surface':
            src = mne.setup_source_space(self.subject, subjects_dir = self.subject_dir, spacing = self.scr_spacing,
                                    add_dist = "patch")

        elif type == 'volumetric':
            src = mne.setup_volume_source_space(subject=self.subject, bem=self.bem,
                                        subjects_dir=self.subject_dir,
                                        add_interpolator=False)

        return src

    def downsampling_dummy(self, leadfield):
        # TODO: GO MARTIN
        #output size = self.N
        test = np.ones((leadfield.shape[0], self.N))
        return test

    def run(self,  activity, append = False):
        #append is when the simulation was already run before and we want to continue to run it

        #this is supposed to do the matrix multiplication leadfield @ activity
        #check wether we downsample here or not, ask Martin and Maria about downsampling
        #maybe this doesnt make sense, maybe calculate leadfields here and not before???

        forward_solution = mne.make_forward_solution(self.info, trans=self.trans, src=self.src, bem=self.bem,
                                meg=False, eeg=True, mindist=0.0)



        leadfield = forward_solution['sol']['data']
        print(leadfield.shape)

        # somewhere here should be the downsampling function
        downsampled = self.downsampling_dummy(leadfield)
        print(downsampled.shape)
        #which type of activity are we expecting here? Firing rates?
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




