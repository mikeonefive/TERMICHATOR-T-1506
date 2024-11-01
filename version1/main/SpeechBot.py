from api.LLM_API import LLM
from speech_processing.SpeechOutput import SpeechOutput
from speech_processing.SpeechRecorder import SpeechRecorder

class SpeechBot:

    def __init__(self, llm, speech_recorder, speech_output) -> None:

        # default messages & quit command list
        self.greeting_message = "Hi, how are you? What can I do for you?"
        self.goodbye_message = "Nice talking to you. See you next time."
        self.waiting_message = "Hold on a second, I'll consult my database"
        self.followup_question = "What else can I do for you?"
        self.quit_commands = ["quit", "exit", "bye", "goodbye", "terminate", "see you"]

        # dependency-injected components
        self.llm = llm
        self.speech_output = speech_output
        self.speech_recorder = speech_recorder
