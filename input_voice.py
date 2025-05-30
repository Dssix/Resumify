import pyttsx3
import speech_recognition as sr

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def takecommand():
    """Listen to the user's voice and convert it to text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        r.pause_threshold = 1.5
        audio = r.listen(source)
        
        try:
            print("Recognizing....")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
        except Exception as e:
            print("Say that again please....")
            return "None"
        return query

# Example usage
if __name__ == "_main_":
    # speak("kindly speak your answer clearly..")
    print("Speak")
    command = takecommand()
    print(f"Recognized Command: {command}")