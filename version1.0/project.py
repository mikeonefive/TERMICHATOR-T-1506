# system and time libraries
import sys
import time

# all necessary libraries to connect to hugging face
from hugchat import hugchat
from dotenv import dotenv_values
from hugchat.login import Login

# speech libraries
import pyttsx3
import speech_recognition

# graphical interface
import pygame

# threading, processes running at the same time
import threading
from concurrent.futures import ThreadPoolExecutor

secrets = dotenv_values("hf.env")
email = secrets["EMAIL"]
passwd = secrets["PASS"]

quit_commands = ["quit", "exit", "bye", "goodbye", "terminate", "see you"]


class ChatBot:

    def __init__(self):
        # connect to HuggingFace API
        signin = Login(email, passwd)
        self.cookies = signin.login()

        # create chatbot/assign HF API
        self.brain = hugchat.ChatBot(cookies=self.cookies.get_dict())

        # initialize voice and set voice properties
        self.speech = pyttsx3.init()
        voices = self.speech.getProperty('voices')
        self.speech.setProperty('voice', voices[0].id)

        # initialize input for speech recognition
        self.record_speech = speech_recognition.Recognizer()
        self.record_speech.dynamic_energy_threshold = True

        self.user_input = None

        # initialize pygame so you can use font and display graphics
        pygame.init()

        window_width = 1280
        window_height = 720

        # initialize window
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Term1chat0r T-1506")
        pygame_icon = pygame.image.load('images/icon.jpg')
        pygame.display.set_icon(pygame_icon)

        # set font for messages
        self.font = pygame.font.SysFont("Arial", 22)

        # show robot picture
        self.image = pygame.image.load('images/robot.png')
        self.screen.blit(self.image, (0, 0))

        # load mouth images into variable
        self.mouth_images = pygame.image.load('images/spritesheet.png').convert_alpha()

        # what time this initially starts to run at, needed for mouth animation
        self.last_update = pygame.time.get_ticks()

        # create animation list, load images for mouth_animation
        self.animation_list = []
        self.frame = 0
        self.animation_cooldown = 100
        animation_steps = 3

        for image in range(animation_steps):
            # get images from spritesheet and append them to a list
            self.animation_list.append(self.get_image(self.mouth_images, image, 49, 46))
            self.screen.blit(self.animation_list[self.frame], (360, 128))

    def generate_answer(self, user_input):
        answer = self.brain.chat(user_input)
        return answer

    # function that records and processes user's spoken input, returns the input
    def speech_input(self):
        with speech_recognition.Microphone() as source:
            self.record_speech.adjust_for_ambient_noise(source)
            recording = self.record_speech.listen(source)
        try:
            self.user_input = self.record_speech.recognize_google(recording)
            print(self.user_input)

        except speech_recognition.UnknownValueError:
            # print("Error: Google Speech Recognition could not understand audio")
            return None  # "no input or input not recognized"

        except speech_recognition.RequestError as error:
            sys.exit("Could not request results from Google Speech Recognition service; {0}".format(error))

        return self.user_input

    def speech_output(self, input_to_speak):
        self.speech.say(input_to_speak)
        self.speech.runAndWait()

    def update_animations(self, is_speaking, is_listening):
        # update animation, if more than 100ms have passed move on to next frame
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame = (self.frame + 1) % len(self.animation_list)
            # reset the cooldown
            self.last_update = current_time

        self.screen.blit(self.image, (0, 0))

        self.frame = 1 if not is_speaking else self.frame
        self.screen.blit(self.animation_list[self.frame], (360, 128))

        if is_listening:
            msg = self.font.render("Speak now!", True, (220, 220, 220))
            self.screen.blit(msg, (800, 80))

        pygame.display.update()

    # get image is a helper method to get a single mouth image from the spritesheet
    @staticmethod
    def get_image(sheet, frame, width, height):
        # frame * width jumps pos x to the next image (specified above as 49)
        rect = pygame.Rect((frame * width), 0, width, height)
        image = sheet.subsurface(rect)
        return image


def main():
    bot = ChatBot()

    thread_speech = threading.Thread(target=bot.speech_output,
                                     args=("Hi, how are you? What can I do for you?",), daemon=True)
    thread_speech.start()

    thread_speech_input = None
    thread_generate_answer = None

    is_speaking = True
    user_input = None
    answer = None

    running = True
    bot.update_animations(is_speaking, False)

    executor = ThreadPoolExecutor()

    """STATE_SPEECH_INPUT_START = 0
    STATE_SPEECH_INPUT = 1
    STATE_CHECK_INPUT = 2
    STATE_GENERATE_ANSWER_START = 3
    STATE_GENERATE_ANSWER = 4
    STATE_SPEECH_OUTPUT_START = 5
    STATE_SPEECH_OUTPUT_NEXT_QUESTION = 6
    STATE_QUIT = 7"""

    current_state = "STATE_SPEECH_INPUT_START"

    while running:

        # if user closes window, terminate program
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                current_state = "STATE_WINDOW_QUIT"

        match current_state:
            case "STATE_SPEECH_INPUT_START":
                if not is_speaking:
                    # submit starts the function and returns a future object,
                    # we can't store the entire thread in user_input, just the result
                    thread_speech_input = executor.submit(bot.speech_input)
                    current_state = "STATE_SPEECH_INPUT"

            case "STATE_SPEECH_INPUT":
                if thread_speech_input.done():
                    user_input = thread_speech_input.result()
                    current_state = "STATE_CHECK_INPUT"

            case "STATE_CHECK_INPUT":
                start_time = time.time()
                if not user_input:
                    current_state = "STATE_SPEECH_INPUT_START"
                elif user_input.strip() in quit_commands:
                    current_state = "STATE_BYE"
                else:
                    current_state = "STATE_GENERATE_ANSWER_START"

            case "STATE_GENERATE_ANSWER_START":
                thread_speech = threading.Thread(target=bot.speech_output,
                                                 args=("Hold on a second, I'll consult my database",), daemon=True)
                thread_speech.start()
                thread_generate_answer = executor.submit(bot.generate_answer, user_input)
                current_state = "STATE_GENERATE_ANSWER"

            case "STATE_GENERATE_ANSWER":
                if thread_generate_answer.done():
                    answer = thread_generate_answer.result()
                    current_state = "STATE_SPEECH_OUTPUT_START"

            case "STATE_SPEECH_OUTPUT_START":
                if not is_speaking:
                    thread_speech = threading.Thread(target=bot.speech_output, args=(answer,), daemon=True)
                    thread_speech.start()
                    current_state = "STATE_SPEECH_OUTPUT_NEXT_QUESTION"

                    # time it took to find answer to the questions
                    seconds = round(time.time() - start_time)
                    print(seconds, "seconds")

            case "STATE_SPEECH_OUTPUT_NEXT_QUESTION":
                if not is_speaking:
                    thread_speech = threading.Thread(target=bot.speech_output,
                                                     args=("What else can I do for you?",), daemon=True)
                    thread_speech.start()
                    current_state = "STATE_SPEECH_INPUT_START"

            case "STATE_BYE":
                if not is_speaking:
                    # Start a separate thread forcing update animations, because we move on to STATE_QUIT
                    # they won't update like in all the other threads because we get into STATE_QUIT too fast
                    thread_animations = threading.Thread(target=bot.update_animations,
                                                         args=(is_speaking, False), daemon=True)
                    thread_animations.start()

                    thread_speech = threading.Thread(target=bot.speech_output,
                                                     args=("Nice talking to you. See you next time.",), daemon=True)
                    thread_speech.start()
                current_state = "STATE_QUIT"

            case "STATE_QUIT":
                if not is_speaking:
                    executor.shutdown(wait=False)
                    running = False

            case "STATE_WINDOW_QUIT":
                executor.shutdown(wait=False)
                running = False

        # check if thread is still running and store in is speaking
        is_speaking = thread_speech.is_alive()
        bot.update_animations(is_speaking, current_state == "STATE_SPEECH_INPUT")

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
