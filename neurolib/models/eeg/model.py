
# comment to test my git skills

class EEGModel:

    def __init__(self, params, N, subject="fsaverage", trans=None, src=None, bem=None, info = None):

        self.subject = subject
        #subject should always be a string
        self.src = src
        self.trans= trans #do we calculate trans if not given?? Or do we use fsaverage trans?
        self.bem = bem
        self.info = info #info gives electrodes positions
        pass


    def loadSubjectData(self):
        open data file
        #have supported data file

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

        pass
