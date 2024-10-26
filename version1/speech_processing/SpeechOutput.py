import pyttsx3


class SpeechOutput:

    def __init__(self) -> None:
        # initialize voice and set voice properties
        self.speech = pyttsx3.init()
        voices = self.speech.getProperty('voices')
        self.speech.setProperty('voice', voices[0].id)

    def say(self, input_to_speak) -> None:
        self.speech.say(input_to_speak)
        self.speech.runAndWait()
