from Requirements import time, sys, pygame, threading, ThreadPoolExecutor


class FiniteStateMachine:

    def __init__(self, speech_bot, animations):
        # instance variables
        self.speech_bot = speech_bot
        self.animations = animations
        self.threadpool = ThreadPoolExecutor()

        # state variables
        self.current_state = "STATE_SPEECH_INPUT_START"
        self.is_speaking = True
        self.is_listening = False
        self.is_running = True

        # result variables
        self.user_input = None
        self.answer = None

        # futures for async task management
        self.thread_speech_input = None
        self.thread_generate_answer = None

        self.thread_speech = threading.Thread(target=speech_bot.speech_output.say,
                                              args=(speech_bot.greeting_message,), daemon=True)
        self.thread_speech.start()

        animations.update_animations(self.is_speaking, self.is_listening)


    # run is like the main method of this class
    def run(self):
        while self.is_running:
            self.handle_window_close_event()

            match self.current_state:
                case "STATE_SPEECH_INPUT_START":
                    self.start_speech_input()

                case "STATE_GET_SPEECH_INPUT":
                    self.get_speech_input_from_user()

                case "STATE_CHECK_INPUT":
                    self.start_time = time.time()
                    self.check_input()

                case "STATE_GENERATE_ANSWER_START":
                    self.start_generating_answer()

                case "STATE_GET_ANSWER":
                    self.get_answer_from_llm()

                case "STATE_SPEECH_OUTPUT_START":
                    self.start_speech_output()

                case "STATE_SPEECH_OUTPUT_NEXT_QUESTION":
                    self.ask_followup_question()

                case "STATE_BYE":
                    self.say_goodbye()

                case "STATE_QUIT":
                    self.shutdown_threadpool()

                case "STATE_WINDOW_QUIT":
                    self.threadpool.shutdown(wait=False)
                    self.is_running = False

            # check if speaking thread is still running and store in is_speaking
            self.is_speaking = self.thread_speech.is_alive()
            self.animations.update_animations(self.is_speaking, self.current_state == "STATE_SPEECH_INPUT")

        pygame.quit()
        sys.exit()


    def handle_window_close_event(self):
        # if user closes window, terminate program
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.current_state = "STATE_WINDOW_QUIT"


    def start_speech_input(self):
        if not self.is_speaking:
            # submit starts the function and returns a future object,
            # we can't store the entire thread in user_input, just the result
            self.thread_speech_input = self.threadpool.submit(self.speech_bot.speech_recorder.process_speech_input)
            self.current_state = "STATE_GET_SPEECH_INPUT"


    def get_speech_input_from_user(self):
        if self.thread_speech_input.done():
            self.user_input = self.thread_speech_input.result()
            self.current_state = "STATE_CHECK_INPUT"


    def check_input(self):
        answer_instruction_addition = " Please keep the answer brief."

        if not self.user_input:
            self.current_state = "STATE_SPEECH_INPUT_START"
        elif self.user_input.replace(answer_instruction_addition, "").strip() in self.speech_bot.quit_commands:
            self.current_state = "STATE_BYE"
        else:
            self.current_state = "STATE_GENERATE_ANSWER_START"


    def start_generating_answer(self):
        self.thread_speech = threading.Thread(target=self.speech_bot.speech_output.say,
                                              args=(self.speech_bot.waiting_message,), daemon=True)
        self.thread_speech.start()
        self.thread_generate_answer = self.threadpool.submit(self.speech_bot.llm.generate_answer, self.user_input)
        self.current_state = "STATE_GET_ANSWER"


    def get_answer_from_llm(self):
        if self.thread_generate_answer.done():
            self.answer = self.thread_generate_answer.result()
            self.current_state = "STATE_SPEECH_OUTPUT_START"


    def start_speech_output(self):
        if not self.is_speaking:
            self.thread_speech = threading.Thread(target=self.speech_bot.speech_output.say,
                                                  args=(self.answer,), daemon=True)
            self.thread_speech.start()
            self.current_state = "STATE_SPEECH_OUTPUT_NEXT_QUESTION"



    def print_elapsed_time(self):
        # time it took to find answer to the current question
        elapsed = (time.time() - self.start_time)
        print(f"Elapsed time: {elapsed:.2f} seconds")


    def ask_followup_question(self):

        if not self.is_speaking:

            self.print_elapsed_time()       # time it took to generate and output the previous answer

            self.thread_speech = threading.Thread(target=self.speech_bot.speech_output.say,
                                                  args=(self.speech_bot.followup_question,), daemon=True)
            self.thread_speech.start()
            self.current_state = "STATE_SPEECH_INPUT_START"


    def say_goodbye(self):
        if not self.is_speaking:
            # Start a separate thread forcing update animations, because we move on to STATE_QUIT
            # they won't update like in all the other threads because we get into STATE_QUIT too fast
            thread_animations = threading.Thread(target=self.animations.update_animations,
                                                 args=(self.is_speaking, False), daemon=True)
            thread_animations.start()

            self.thread_speech = threading.Thread(target=self.speech_bot.speech_output.say,
                                                  args=(self.speech_bot.goodbye_message,), daemon=True)
            self.thread_speech.start()

        self.current_state = "STATE_QUIT"


    def shutdown_threadpool(self):
        if not self.is_speaking:
            self.threadpool.shutdown(wait=False)
            self.is_running = False
