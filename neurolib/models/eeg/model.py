import numpy as np
import mne
import os.path as op
from . import loadDefaultParams as dp



class EEGModel:

    def __init__(self, params):
        """
        sfreq refers to the sample rate of the data using when creating the info file with the montage
        """

        params_eeg = dp.loadDefaultParams(conductances = params.get(
            "eeg_conductances"),
                                      type_scr = params.get("eeg_type_scr"),
                                      scr_pos=params.get("eeg_scr_pos"),
                                      scr_spacing=params.get("eeg_scr_spacing"),
                                      sfreq = params.get("eeg_montage_sfreq")
                                      )

        self.conductances = params_eeg.eeg_conductances
        self.type_scr = params_eeg.eeg_type_scr
        self.scr_pos = params_eeg.eeg_scr_pos
        self.scr_spacing = params_eeg.eeg_scr_spacing
        self.sfreq = params_eeg.eeg_montage_sfreq

        self.N = params.get("N")  # this is number of nodes
        # TODO: somwhere compare N with the number of regions in the atlas. Assert they are the same

        # Since the user should only be able to change the conductances, the type of the sources and the pos/spacing
        # we only need to have in the loadDefaultParams.py those four values.


        # TODO: When the user doesnt change all params accordingly we should give a warning saying it's gonna run with default values

        self.subject_dir = "../../data/datasets/eeg_fsaverage"
        self.subject = 'fsaverage'
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


        #attributes needed to make forward solution
        self.mindist = 0.0
        self.ignore_ref = False # we don't understand this
        self.n_jobs = 1
        self.N = params.N # this is number of nodes

        self.EEG = None
        self.t_EEG = None
        #everything that the user can change should go to params

    # TODO: handlining standart parameter differntly
    def set_bem(self, ico = 4, conductivity = (0.3,0.006, 0.3), verbose = None):
        print("If you set the volumetric source with the bem before this, do it again! Otherwise, it's using the bem from the fsaverage!!")


    def set_bem(self):
        model = mne.make_bem_model(self.subject, ico = 4, conductivity = self.conductances,
                                   subjects_dir = self.subject_dir)
        bem = mne.make_bem_solution(model)
        return bem

    def set_src(self):
        type = self.type_scr
        if type == 'surface':

            spacing = kwargs.get("spacing", 'oct6')
            add_dist = kwargs.get("add_dist", 'patch')
            self.n_jobs = kwargs.get("n_jobs", 1)
            surface = kwargs.get("surface",'white')
            verbose = kwargs.get("verbose", None)

            self.src = mne.setup_source_space(self.subject,
                                              subject_dir=self.subject_dir,
                                              spacing=spacing,
                                              add_dist=add_dist,
                                              n_jobs=self.n_jobs,
                                              surface = surface,
                                              verbose = verbose)

            src = mne.setup_source_space(self.subject, subject_dir = self.subject_dir, spacing = self.scr_spacing,
                                    add_dist = "patch")


        if type == 'volumetric':
            src = mne.setup_volume_source_space(subject=self.subject, bem=self.bem,
                                        subjects_dir=self.subject_dir,
                                        add_interpolator=False)
        return src

    def downsampling(self):
        # TODO: GO MARTIN
        #output size = self.N
        pass

    def run(self,  activity, append = False):
        #append is when the simulation was already run before and we want to continue to run it

        #this is supposed to do the matrix multiplication leadfield @ activity
        #check wether we downsample here or not, ask Martin and Maria about downsampling
        #maybe this doesnt make sense, maybe calculate leadfields here and not before???

        forward_solution = mne.make_forward_solution(self.info, trans=self.trans, src=self.src, bem=self.bem,
                                meg=False, eeg=True, mindist=0.0)



        leadfield = forward_solution['sol']['data']

        # somewhere here should be the downsampling function

        downsampled = self.downsampling(self, leadfield, atlas=None,
                                       averaging_method=None)


        #which type of activity are we expecting here? Firing rates?
        # we need to think about units, it's in mV, conductivities also have units.
        # activity should probably be in Hz, not kHz as in aln.
        # Hopf has no units
        # Try first with aln, and figure out the correct scale. Then figure out other models without units.
        

        result = downsampled @ activity
        return result

    pass




