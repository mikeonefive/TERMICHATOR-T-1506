import os

from dotenv import dotenv_values
from hugchat import hugchat
from hugchat.login import Login


class LLM:

    def __init__(self):
        # secrets = dotenv_values("hf.env") if the file is located in current working directory
        # get the absolute path to hf.env based on the script's location
        env_path = os.path.join(os.path.dirname(__file__), "hf.env")
        secrets = dotenv_values(env_path)
        email = secrets["EMAIL"]
        passwd = secrets["PASS"]

        # connect to HuggingFace API
        signin = Login(email, passwd)
        self.cookies = signin.login()

        # create chatbot/assign HF API
        self.brain = hugchat.ChatBot(cookies=self.cookies.get_dict())

    # gets the answer from the API
    def generate_answer(self, user_input):
        answer = self.brain.chat(user_input)
        return answer
