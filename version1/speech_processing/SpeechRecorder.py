import speech_recognition
import sys


class SpeechRecorder:

    def __init__(self):
        self.record_speech = speech_recognition.Recognizer()
        self.record_speech.dynamic_energy_threshold = True

    # function that records and processes user's spoken input, returns the input
    def speech_input(self):
        with speech_recognition.Microphone() as source:
            self.record_speech.adjust_for_ambient_noise(source)
            recording = self.record_speech.listen(source)
        try:
            user_input = self.record_speech.recognize_google(recording)
            print(user_input)

        except speech_recognition.UnknownValueError:
            # print("Error: Google Speech Recognition could not understand audio")
            return None  # "no input or input not recognized"

        except speech_recognition.RequestError as error:
            sys.exit("Could not request results from Google Speech Recognition service; {0}".format(error))

        return user_input
