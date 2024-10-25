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