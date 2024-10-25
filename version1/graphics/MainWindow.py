from constants.WindowSize import *
import pygame


class MainWindow:

    def __init__(self):
        # initialize pygame so you can use font and display graphics
        pygame.init()

        # initialize window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Term1chat0r T-1506")
        pygame_icon = pygame.image.load('images/icon.jpg')
        pygame.display.set_icon(pygame_icon)

        # set font for messages
        self.font = pygame.font.SysFont("Arial", 22)

        # show robot picture
        self.image = pygame.image.load('images/robot.png')
        self.screen.blit(self.image, (0, 0))
