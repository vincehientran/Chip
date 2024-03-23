import speech_recognition as sr  

class Speech(object):
    def __init__(self):                                                                     
        r = sr.Recognizer()                                                                                   
        with sr.Microphone() as source:                                                                       
            while True:
                try:
                    audio = r.listen(source, timeout=2) 
                    print(r.recognize_google(audio))
                except:
                    continue