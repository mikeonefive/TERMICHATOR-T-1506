from Requirements import time, sys, pygame, threading, ThreadPoolExecutor

from gui.MainWindow import MainWindow
from gui.Animations import Animations
from SpeechBot import *


def main() -> None:

    main_window = MainWindow()              # initialize pygame, main window, and display background picture

    animations = Animations(main_window)    # everything that has to do with mouth animations

    # instantiate dependencies for the chatbot (speech analysis, speech output and the LLM)
    llm = LLM()
    speech_output = SpeechOutput()
    speech_recorder = SpeechRecorder()

    # inject dependencies into chatbot
    speech_bot = SpeechBot(llm=llm, speech_recorder=speech_recorder, speech_output=speech_output)

    # TODO change the threading approach, if possible use a separate class?
    thread_speech = threading.Thread(target=speech_bot.speech_output.say,
                                     args=(speech_bot.greeting_message,), daemon=True)
    thread_speech.start()

    thread_speech_input = None
    thread_generate_answer = None

    user_input = None
    answer = None

    is_speaking = True
    is_listening = False
    is_running = True
    animations.update_animations(is_speaking, is_listening)

    executor = ThreadPoolExecutor()

    current_state = "STATE_SPEECH_INPUT_START"

    while is_running:

        # if user closes window, terminate program
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                current_state = "STATE_WINDOW_QUIT"

        match current_state:
            case "STATE_SPEECH_INPUT_START":
                if not is_speaking:
                    # submit starts the function and returns a future object,
                    # we can't store the entire thread in user_input, just the result
                    thread_speech_input = executor.submit(speech_bot.speech_recorder.process_speech_input)
                    current_state = "STATE_SPEECH_INPUT"

            case "STATE_SPEECH_INPUT":
                if thread_speech_input.done():
                    user_input = thread_speech_input.result()
                    current_state = "STATE_CHECK_INPUT"

            case "STATE_CHECK_INPUT":
                start_time = time.time()
                answer_instruction_addition = " Please keep the answer brief."

                if not user_input:
                    current_state = "STATE_SPEECH_INPUT_START"
                elif user_input.replace(answer_instruction_addition, "").strip() in speech_bot.quit_commands:
                    current_state = "STATE_BYE"
                else:
                    current_state = "STATE_GENERATE_ANSWER_START"

            case "STATE_GENERATE_ANSWER_START":
                thread_speech = threading.Thread(target=speech_bot.speech_output.say,
                                                 args=(speech_bot.waiting_message,), daemon=True)
                thread_speech.start()
                thread_generate_answer = executor.submit(speech_bot.llm.generate_answer, user_input)
                current_state = "STATE_GENERATE_ANSWER"

            case "STATE_GENERATE_ANSWER":
                if thread_generate_answer.done():
                    answer = thread_generate_answer.result()
                    current_state = "STATE_SPEECH_OUTPUT_START"

            case "STATE_SPEECH_OUTPUT_START":
                if not is_speaking:
                    thread_speech = threading.Thread(target=speech_bot.speech_output.say, args=(answer,), daemon=True)
                    thread_speech.start()
                    current_state = "STATE_SPEECH_OUTPUT_NEXT_QUESTION"

                    # time it took to find answer to the questions
                    seconds = round(time.time() - start_time)
                    # print(seconds, "seconds")

            case "STATE_SPEECH_OUTPUT_NEXT_QUESTION":
                if not is_speaking:
                    thread_speech = threading.Thread(target=speech_bot.speech_output.say,
                                                     args=(speech_bot.followup_question,), daemon=True)
                    thread_speech.start()
                    current_state = "STATE_SPEECH_INPUT_START"

            case "STATE_BYE":
                if not is_speaking:
                    # Start a separate thread forcing update animations, because we move on to STATE_QUIT
                    # they won't update like in all the other threads because we get into STATE_QUIT too fast
                    thread_animations = threading.Thread(target=animations.update_animations,
                                                         args=(is_speaking, False), daemon=True)
                    thread_animations.start()

                    thread_speech = threading.Thread(target=speech_bot.speech_output.say,
                                                     args=(speech_bot.goodbye_message,), daemon=True)
                    thread_speech.start()
                current_state = "STATE_QUIT"

            case "STATE_QUIT":
                if not is_speaking:
                    executor.shutdown(wait=False)
                    is_running = False

            case "STATE_WINDOW_QUIT":
                executor.shutdown(wait=False)
                is_running = False

        # check if thread is still is_running and store in is speaking
        is_speaking = thread_speech.is_alive()
        animations.update_animations(is_speaking, current_state == "STATE_SPEECH_INPUT")

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
