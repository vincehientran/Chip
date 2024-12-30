import os
import pickle
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import logging

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class AudioRecorder:
    def __init__(self):
        self.sampling_frequency = 44100

    def record(self, seconds: int = 10):
        audio_data = sd.rec(int(seconds * self.sampling_frequency), samplerate=self.sampling_frequency, channels=1, dtype='float64')
        sd.wait()
        return audio_data

    def save_as_wav(self, audio_data, filename):
        wav.write(filename, self.sampling_frequency, np.asarray(audio_data))

class SpeechRecognition:
    def __init__(self) -> None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.resPath = os.path.join(script_dir, '..', '..', 'res') + os.path.sep

        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)

    def load_model(self):
        '''
        Load model from storage or download model if it doesn't exist.
        '''

        if os.path.exists(self.resPath+'model-Llama-3.2-3B-Instruct'):
            print('loading model from save')
            return AutoModelForCausalLM.from_pretrained(self.resPath+'model-Llama-3.2-3B-Instruct')
        else:
            print('downloading model')
            model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", torch_dtype="auto", trust_remote_code=True)
            print('saving model')
            model.save_pretrained(self.resPath+'model-Llama-3.2-3B-Instruct')
            return model
            
    def load_tokenizer(self):
        '''
        Load tokenizer from storage or download tokenizer if it doesn't exist.
        '''

        if os.path.exists(self.resPath+'tokenizer-Llama-3.2-3B-Instruct'):
            print('loading tokenizer from save')
            return AutoTokenizer.from_pretrained(self.resPath+'tokenizer-Llama-3.2-3B-Instruct')
        else:
            print('downloading tokenizer')
            tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", trust_remote_code=True)
            print('saving tokenizer')
            tokenizer.save_pretrained(self.resPath+'tokenizer-Llama-3.2-3B-Instruct')
            return tokenizer
    

torch.set_default_device("cuda")

script_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_dir, '..', '..', 'res') + os.path.sep
sr = SpeechRecognition()
model = sr.load_model()
tokenizer = sr.load_tokenizer()

system_context_path = os.path.join(script_dir, '..', '..', 'res') + os.path.sep + 'system-context.txt'
system_context = ''
with open(system_context_path, "r", encoding="utf-8") as file:
    system_context = file.read()

pipe = pipeline(
    "text-generation", 
    model=model, 
    tokenizer=tokenizer, 
    torch_dtype=torch.bfloat16, 
    device_map="auto",
    pad_token_id=tokenizer.eos_token_id,
)

messages = [
    {"role": "system", "content": "Base System Knowlege: Chip is a small friendly robot. Chip also speaks in 3rd person and refers to itself as \"Chip\" instead of \"I\". Chip doesn't ramble a lot and Chip just speaks in normal length responses. Chip also doesn't use those roleplay text such as *laughs*. Chip just speaks normally. KNOWLEGE LIST:" + system_context},
]

while (text := input('\nMe: ')) != 'q':
    messages.append({'role': 'user','content': text})
    outputs = pipe(
        messages,
        max_new_tokens=512,
        num_return_sequences=1
    )
    response = outputs[0]["generated_text"][-1]['content']
    messages.append({'role': 'assistant','content': response})
    print('\nChip: '+response)

messages.append({'role': 'user','content': 'Summarize new things in this conversation by listing all of the things that the user told assistant about user, user told assistant about assistant, and assistant told user about assistant. Assistant is Chip. Only list things that are important to remember long term, such as personality traits, physical traits, etc. Continue the KNOWLEGE LIST from the system context. \n For example, 1. the user\'s name is ___. 2. (User\'s name) likes to ____. 3. Chip is ____. 4. Chip likes to do ____. '})
outputs = pipe(
        messages,
        max_new_tokens=512,
        num_return_sequences=1
    )
response = outputs[0]["generated_text"][-1]['content']
print(response)

with open(system_context_path, "w", encoding="utf-8") as file:
    file.write(response)

# if __name__ == "__main__":
#     recorder = AudioRecorder()
#     audio_data = recorder.record()
#     recorder.save_as_wav(audio_data, "recorded_audio.wav")
