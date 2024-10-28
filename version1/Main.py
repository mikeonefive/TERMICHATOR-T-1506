from gui.MainWindow import MainWindow
from gui.Animations import Animations
from SpeechBot import *
from FiniteStateMachine import FiniteStateMachine


def main() -> None:

    # initialize pygame, main window, and display background picture
    main_window = MainWindow()

    # everything that has to do with mouth animations
    animations = Animations(main_window)

    # instantiate dependencies for the chatbot (speech analysis, speech output and the LLM)
    llm = LLM()
    speech_output = SpeechOutput()
    speech_recorder = SpeechRecorder()

    # inject necessary dependencies into chatbot
    speech_bot = SpeechBot(llm=llm, speech_recorder=speech_recorder, speech_output=speech_output)

    # A Finite State Machine (FSM) is like a simple computer that can be in different states at different times
    # it follows a set of rules to move from one state to another based on inputs it receives (e.g. traffic lights 3 colors and changing states based on sensors)
    # FSMs help control how things happen in a system step by step
    fsm = FiniteStateMachine(speech_bot, animations)
    fsm.run()   # run is the real main method here, has the game loop and everything


if __name__ == "__main__":
    main()
