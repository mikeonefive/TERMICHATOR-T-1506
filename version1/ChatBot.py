from Requirements import *

from graphics.MainWindow import MainWindow

from ChatbotCommands import *

from LLM_API import LLM
from speech_processing.SpeechModule import SpeechModule
from speech_processing.SpeechRecorder import SpeechRecorder


class ChatBot:

    def __init__(self):

        # initialize connection to LLM
        self.llm = LLM()

        self.quit_commands = ChatbotCommands().get_quit_commands()

        # initialize speech module
        self.speech = SpeechModule().speech

        # initialize input for speech recognition
        self.record_user_speech_input = SpeechRecorder().record_speech

        self.user_input = None

        # initialize pygame & main window
        self.main_window = MainWindow()

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
            self.main_window.screen.blit(self.animation_list[self.frame], (360, 128))

    def generate_answer(self, user_input):
        answer = self.llm.brain.chat(user_input)
        return answer

    # function that records and processes user's spoken input, returns the input
    def speech_input(self):
        with speech_recognition.Microphone() as source:
            self.record_user_speech_input.adjust_for_ambient_noise(source)
            recording = self.record_user_speech_input.listen(source)
        try:
            self.user_input = self.record_user_speech_input.recognize_google(recording)
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

        self.main_window.screen.blit(self.main_window.image, (0, 0))

        self.frame = 1 if not is_speaking else self.frame
        self.main_window.screen.blit(self.animation_list[self.frame], (360, 128))

        if is_listening:
            msg = self.main_window.font.render("Speak now!", True, (220, 220, 220))
            self.main_window.screen.blit(msg, (800, 80))

        pygame.display.update()

    # get image is a helper method to get a single mouth image from the spritesheet
    @staticmethod
    def get_image(sheet, frame, width, height):
        # frame * width jumps pos x to the next image (specified above as 49)
        rect = pygame.Rect((frame * width), 0, width, height)
        image = sheet.subsurface(rect)
        return image