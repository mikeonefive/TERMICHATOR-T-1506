# TERMICHATOR T-1506
    #### Video Demo: https://youtu.be/ldLo9zOm16A
    #### Description:
    The TERMICHATOR T-1506 is an AI chatbot/personal assistent which uses speech recognition and text-to-speech libraries. That means it's possible to have entire conversations with it, either by asking questions or providing any other kind of input.

If we take a look at the project, the first thing that is created is a class called ChatBot which includes all the necessary methods for the TERMICHATOR to work. One of its core features consists of connecting to an LLM via the Hugging Face online chat AI (the current model is meta-llama/Llama-2-70b-chat-hf, as of October 2023). This acts as the TERMICHATOR'S brain and knowledge database. 
In the next step, the __init__ method initializes and sets up the voice properties with the help of the pyttsx3 library which ensures that the text to speech output works. Furthermore, in order to be able to recognize speech as user input, it uses the Google speech 
recognition library.
As an additional feature, the TERMICHATOR also features a GUI which was implemented using the pygame library. It consists of a window which shows a picture of the robot that appears to be talking. This is achieved through a more or less simple animation of pictures of different mouth frames. These frames will move and change as long as the robot is speaking, thus simulating a talking entity. It was crucial to use threading to a certain extent here in order to make sure the animations and audio output work in sync.

At the start of the program, the user is greeted with a friendly welcome message. Additionally the TERMICHATOR will ask what it can do for the user. At this point it is time to interact with the chatbot since it is now possible to ask questions or provide input for it to handle. The GUI will let the user know, when to speak into the microphone with an on-screen message, meaning that speech recognition is ready to process the user's input. The TERMICHATOR will remain in, or rather go back to this same state and wait for input by the user.  

After it has successfully received input from the user, the program then calls the method generate_answer which connects to the Hugging Face API and thus tries to find an answer to the question or input provided. This can take some time, so the chatbot will always let the user know that it is about to consult its database and then output the answer via text to speech as soon as it has been processed and is ready. After the output was successful, the game loop reverts back to the speech input stage, meaning the user can ask another question or rather continue the conversation with the AI. This will continue until the user decides to quit the application. 

Finally, there are two ways to quit the application. One can either just close the GUI window, thus effectively shutting down the TERMICHATOR immediately. But in addition to that, a list of quit commands which the chatbot reacts to, was implemented. Examples of such commands include "quit", "bye" or "terminate". If the chatbot recognizes one of said commands, it will respond by also saying "goodbye" to the user before exiting the program.

So here it is, ladies and gentlemen, put your hands up for the TERMICHATOR T-1506!
