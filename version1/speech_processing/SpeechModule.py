import pyttsx3


class SpeechModule:

    def __init__(self):
        # initialize voice and set voice properties
        self.speech = pyttsx3.init()
        voices = self.speech.getProperty('voices')
        self.speech.setProperty('voice', voices[0].id)

