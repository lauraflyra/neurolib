import numpy as np
import mne
import neurolib.models.eeg.loadDefaultParams as dp
from neurolib.utils.collections import dotdict
from neurolib.models.eeg.eeg_util import downsample_leadfield_matrix, get_labels_of_points
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
        self.params_eeg.eeg_atlas = params.get("eeg_atlas")

        self.forward_solution = None
        self.leadfield = None
        self.unique_labels = None   # region labels that the leadfield matrix columns correspond to

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

        self.N = params.get("N")  # this is number of nodes
        # Remark: here a check if self.N == regions of desired atlas would make sense. It requires a homogeneous
        #  definition of the atlases/ number of region information.
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

        default_lf_files = np.load(os.path.join(self.subject_dir, "default_leadfield.npz"))
        self.unique_labels = default_lf_files["unique_labels"]
        self.leadfield = default_lf_files["leadfield_downsampled"]

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

    def downsampling(self):
        """ This function takes in a forward solution that was computed for a surface source space. First, the forward
            solution is converted to a solution of fixed dipole orientation. Then, each dipole is assigned to an atlas
            region. Afterwards, all columns of the leadfield matrix that correspond to dipoles of the same region, are
            averaged. The resulting leadfield matrix has the dimensions electrodes x atlas regions.

            :return:    Array of region-codes of the atlas and down sampled leadfield matrix with the columns sorted
                        according to the region-codes in the array 'unique_labels'.
            :rtype:     tuple[np.ndarray, np.ndarray]
        """

        # Fix the dipole orientation to surface normal. Requires surface source space for orientation information.
        # This step results in a number of dipoles equal to the number of source locations.
        fwd_fixed = mne.convert_forward_solution(self.forward_solution, surf_ori=True, force_fixed=True,
                                                 use_cps=True)

        if len(fwd_fixed["src"]) == 2:  # surface source space is divided into two hemispheres in mne

            # 0 is left, 1 is right hemisphere
            lh = fwd_fixed['src'][0]
            dip_pos_lh = np.vstack(lh['rr'][lh['vertno']])
            rh = fwd_fixed['src'][1]
            dip_pos_rh = np.vstack(rh['rr'][rh['vertno']])

            if dip_pos_lh.shape != dip_pos_rh.shape:
                raise ValueError("Both hemispheres should contain the same number of sources.")

            dip_pos = np.vstack((dip_pos_lh, dip_pos_rh))
        else:
            raise ValueError("Other format than expected for a surface source space for whole brain. Two hemispheres "
                             "expected")

        if self.trans == "fsaverage":
            trans_path = os.path.join(self.subject_dir, "fsaverage", "bem", "fsaverage-trans.fif")
            trafo = mne.read_trans(trans_path)
        else:
            trafo = mne.read_trans(self.trans)

        dip_pos_mni = mne.head_to_mni(dip_pos, subject=self.subject, mri_head_t=trafo)   # convert from RAS to MNI space

        points_found, label_codes, label_strings = get_labels_of_points(dip_pos_mni, atlas=self.params_eeg.eeg_atlas)

        leadfield_full = fwd_fixed['sol']['data']
        unique_labels, leadfield_downsampled = downsample_leadfield_matrix(leadfield_full, label_codes)

        return unique_labels, leadfield_downsampled

    def run(self, activity, append=False):
        # append is when the simulation was already run before and we want to continue to run it

        if self.forward_solution is None:
            self.forward_solution = mne.make_forward_solution(self.info, trans=self.trans, src=self.src, bem=self.bem,
                                                              meg=False, eeg=True, mindist=0.0)

        if self.leadfield is None:
            self.unique_labels, self.leadfield = self.downsampling()

        # TODO: insert in the README info about the transformations used

        EEG_output = self.leadfield @ activity

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
