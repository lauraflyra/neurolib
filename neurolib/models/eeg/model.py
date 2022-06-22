import numpy as np
import mne
import os.path as op
from . import loadDefaultParams as dp



class EEGModel:

    def __init__(self, params):

        params = dp.loadDefaultParams(conductances = params.get("eeg_conductances"),
                                      type_scr = params.get("eeg_type_scr"),
                                      scr_pos=params.get("eeg_scr_pos"),
                                      scr_spacing=params.get("eeg_scr_spacing")
                                      )

        self.conductances = params.eeg_conductances
        self.type_scr = params.eeg_type_scr
        self.scr_pos = params.eeg_scr_pos
        self.scr_spacing = params.eeg_scr_spacing


        # Since the user should only be able to change the conductances, the type of the sources and the pos/spacing
        # we only need to have in the loadDefaultParams.py those three values.


        # TODO: When the user doesnt change all params accordingly we should give a warning saying it's gonna run with default values
        # TODO: Define where is the fsaverage directory

        #TODO: See if we actually need all those parameters as attributes, or if we just need to pass them once, and hence they are unnecessary

        #fs_dir = fetch_fsverage(verbose=True)

        self.subjects_dir = op.dirname(fs_dir)
        #TODO: treat subject and trans file as the same thing, we should always have one trans file per subject
        self.subject = 'fsaverage' #TODO: understand what does subject = 'fsaverage' do
        self.subject_dir = None #TODO: understand that if the subject is fsaverage, if we actually need a subject directory
        self.trans = 'fsaverage' #TODO: understand what does trans = 'fsaverage' do

        self.src = op.join(fs_dir, 'bem', 'fsaverage-ico-5-src.fif') # TODO: make our own source model, maybe then we can keep the function set_scr
        self.bem = op.join(fs_dir, 'bem', 'fsaverage-5120-5120-5120-bem-sol.fif') # TODO: make our own BEM model, maybe then we can keep the function set_bem

        # TODO: Does mne.setup_volume_source_space always require a subject_dir?

        self.kind = "standard_1020"

        montage = mne.channels.make_standard_montage(self.kind, head_size='auto')
        info = mne.create_info(ch_names=montage.ch_names, sfreq=100., ch_types='eeg')
        info.set_montage(montage)


        self.loadRawData()
        
        #attributes needed to make forward solution
        self.mindist = 0.0
        self.ignore_ref = False #we don't understand this
        self.n_jobs = 1
        self.N = N #this is number of nodes

        #everything that the user can change should go to params



 ##########################################
        # First draft that was temporarily rejected
        #
        #
        # self.subject = subject
        #
        # # subject should always be a string
        # # assert subject is string
        #
        # self.subject_dir = subject_dir
        # # have supported data file and path
        #
        # self.src = src
        # # assert src is correct file type
        # self.trans = trans  # do we calculate trans if not given?? Or do we use fsaverage trans?
        # self.bem = bem
        # # assert bem is correct file type
        #
        # if self.subject == "fsaverage":
        #     self.loadSubjectData()
        #
        # self.raw_fname = raw_fname #info gives electrodes positions
        # #check that raw_fname is in the correct format
        # # assert raw_fname is edf file
        #
        # if self.raw_fname is None:
        #     # we use what's in example in mne
        #     self.raw_fname, = eegbci.load_data(subject=1, runs=[6])
        # self.loadRawData()
        # pass

    #
    # def loadSubjectData(self):
    #
    #     fs_dir = fetch_fsverage(verbose=True)
    #     subjects_dir = op.dirname(fs_dir)
    #     self.trans = "fsaverage"
    #     if self.src is None:
    #         self.src = op.join(fs_dir, 'bem', 'fsaverage-ico-5-src.fif')
    #     if self.bem is None:
    #         self.bem = op.join(fs_dir, 'bem', 'fsaverage-5120-5120-5120-bem-sol.fif')
    #


    def loadRawData(self, montage_name='standard_1005'):
        self.raw = mne.io.read_raw_edf(self.raw_fname, preload=True)

        # Clean channel names to be able to use a standard 1005 montage
        # check how this would be for a diff montage!
        if montage_name == 'standard_1005':
            new_names = dict(
                (ch_name,
                 ch_name.rstrip('.').upper().replace('Z', 'z').replace('FP', 'Fp'))
                for ch_name in raw.ch_names)
            self.raw.rename_channels(new_names)
        else:
            pass

        # Read and set the EEG electrode locations, which are already in fsaverage's
        # space (MNI space) for standard_1020:
        montage = mne.channels.make_standard_montage(montage_name)
        self.raw.set_montage(montage)
        self.raw.set_eeg_reference(projection=True)  # needed for inverse modeling

    def set_subject_and_trans(self, subject, subject_dir, trans):
        #do some assertions here
        self.subject = subject
        self.subject_dir = subject_dir
        self.trans = trans

        print("If you change here, you should check that bem/trans/raw are accordingly modified")

    def set_bem(self, ico = 4, conductivity = (0.3,0.006, 0.3), verbose = None):
        print("If you set the volumetric source with the bem before this, do it again! Otherwise, it's using the bem from the fsaverage!!")

        model = mne.make_bem_model(self.subject, ico = ico, conductivity = conductivity,
                                   subjects_dir = self.subjects_dir, verbose = verbose)
        self.bem = mne.make_bem_solution(model)

    def set_src(self, type = 'volumetric', **kwargs):
        if type == 'surface':
            spacing = kwargs.get("spacing", 'oct6')
            add_dist = kwargs.get("add_dist", 'patch')
            self.n_jobs = kwargs.get("n_jobs", 1)
            surface = kwargs.get("surface",'white')
            verbose = kwargs.get("verbose", None)

            self.src = mne.setup_source_space(self.subject, subject_dir = self.subject_dir, spacing = spacing,
                                    add_dist = add_dist, n_jobs = n_jobs, surface = surface, verbose = verbose)

        if type == 'volumetric':

            pos = kwargs.get("pos", 5.0)
            mri = kwargs.get("mri",None)
            sphere = kwargs.get("sphere", None)
            bem = self.bem
            surface = kwargs.get("surface", None)
            self.mindist = kwargs.get("mindist",5.0)
            exclude = kwargs.get("exclude", 0.)
            volume_label = kwargs.get("volume_label", None)
            add_interpolator = kwargs.get("add_interpolator", True)
            sphere_units = kwargs.get("sphere_units", 'm')
            single_volume = kwargs.get("single_volume", False)
            verbose = kwargs.get("verbose", None)

            self.src = mne.setup_volume_source_space(subject=self.subject, pos=pos, mri=mri, sphere=sphere, bem=bem,
                                        surface=surface,mindist=self.mindist, exclude=exclude,
                                        subjects_dir=self.subjects_dir, volume_label=volume_label,
                                        add_interpolator=add_interpolator,sphere_units=sphere_units,
                                        single_volume=single_volume, verbose=verbose)

        #if the person wants to know which kwargs to use, they should refer to the mne library



    # def set_trans(self):
    #
    #     print("You can do it yourself using mne.gui.corregistration!")
    #
    #     print("If you change here, you should check that bem/trans/raw are accordingly modified")
    #     pass

    def set_raw(self, raw_fname, montage_name='standard_1005'):
        self.raw_fname = raw_fname
        self.loadRawData(montage_name=montage_name)

    def downsampling(self):
        #output size = self.N
        pass

    def run(self,  activity, append = False):
        #append is when the simulation was already run before and we want to continue to run it
        
        
        #this is supposed to do the matrix multiplication leadfield @ activity
        #check wether we downsample here or not, ask Martin and Maria about downsampling
        #maybe this doesnt make sense, maybe calculate leadfields here and not before???


        forward_solution = mne.make_forward_solution(self.raw.info, trans=self.trans, src=self.src, bem=self.bem,
                                meg=False, eeg=True, mindist=self.mindist, n_jobs=self.n_jobs,
                                verbose=True)

        leadfield = forward_solution['sol']['data']

        
        # somewhere here should be the downsampling function
        downsampled = downsampling(self, leadfield, atlas, averaging_method)

        #which type of activity are we expecting here? Firing rates?
        # we need to think about units, it's in mV, conductivities also have units.
        # activity should probably be in Hz, not kHz as in aln.
        # Hopf has no units
        # Try first with aln, and figure out the correct scale. Then figure out other models without units.
        

        result = downsampled @ activity
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
