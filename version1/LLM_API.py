from dotenv import dotenv_values
from hugchat import hugchat
from hugchat.login import Login


class LLM:

    def __init__(self):

        secrets = dotenv_values("hf.env")
        email = secrets["EMAIL"]
        passwd = secrets["PASS"]

        # connect to HuggingFace API
        signin = Login(email, passwd)
        self.cookies = signin.login()

        # create chatbot/assign HF API
        self.brain = hugchat.ChatBot(cookies=self.cookies.get_dict())
