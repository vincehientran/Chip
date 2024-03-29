import os
import whisper
import pickle
import warnings

# Suppress UserWarning regarding FP16
warnings.filterwarnings('ignore', category=UserWarning)

resPath = './../../res/'
modelType = 'tiny.en'

def load_model():
    if os.path.exists(resPath+'model-'+modelType+'.pkl'):
        print('loading model from save')
        with open(resPath+'model-'+modelType+'.pkl', "rb") as f:
            return pickle.load(f)
    else:
        print('downloading model')
        model = whisper.load_model(modelType)
        print('saving model')
        with open(resPath+'model-'+modelType+'.pkl', 'wb') as f:
            pickle.dump(model, f)
        return model

def main():
    model = load_model()

    print('transcribing')
    result = model.transcribe(resPath+'audio.mp3')
    print(result['text'])

if __name__ == '__main__':
    main()
