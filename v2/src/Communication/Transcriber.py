import os
import whisper
import pickle
import warnings

class Transcriber:
    '''
    Transcriber can be used to transcribe an audio file into english text using OpenAi Whisper

    Example:
    transcriber = Transcriber('tiny.en')
    print('transcribing')
    result = transcriber.transcribe('./../../res/audio.mp3')
    print(result)
    '''

    def __init__(self, modelType: str) -> None:
        '''
        Initialize a Transcriber object with the specified model type.

        Args:
            modelType (str): The type of the model to be used for transcription. 
                            Possible values are 'tiny', 'base', 'tiny.en', 'base.en'.

        Raises:
            ValueError: If an invalid model type is provided.
        '''
        if modelType not in ['tiny', 'base', 'tiny.en', 'base.en']:
            raise ValueError("Invalid model type. Supported values are 'tiny', 'base', 'tiny.en', 'base.en'.")

        # Suppress UserWarning regarding FP16
        warnings.filterwarnings('ignore', category=UserWarning)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.resPath = os.path.join(script_dir, '..', '..', 'res') + os.path.sep
        
        self.modelType = modelType

        self.model = self.__private_load_model()


    def __private_load_model(self):
        '''
        Load model from storage or download model if it doesn't exist.
        '''

        if os.path.exists(self.resPath+'model-'+self.modelType+'.pkl'):
            print('loading model from save')
            with open(self.resPath+'model-'+self.modelType+'.pkl', "rb") as f:
                return pickle.load(f)
        else:
            print('downloading model')
            model = whisper.load_model(self.modelType)
            print('saving model')
            with open(self.resPath+'model-'+self.modelType+'.pkl', 'wb') as f:
                pickle.dump(model, f)
            return model
        
    def transcribe(self, path: str) -> str:
        '''
        Transcribe audio file located at the path.

        Args:
            path (str): The path to the audio file to be transcribed.

        Returns:
            str: The transcribed text extracted from the audio file.
        '''

        return self.model.transcribe(path)['text']

