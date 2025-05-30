import pyttsx3  # Used to convert texts to speech

engine = pyttsx3.init()   # initilize pyttsx

# Take text and speak it
def speak(text):
    engine.setProperty('rate', 175)  # Reduce speed (Default ~200 WPM)
    engine.say(text)
    engine.runAndWait()