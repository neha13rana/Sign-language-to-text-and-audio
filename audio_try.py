from gtts import gTTS
import playsound

text = "Hello, this is a text-to-speech example in Python."

# Initialize the text-to-speech engine
tts = gTTS(text)

# Save the speech to a temporary file
tts.save("output.mp3")

# Play the speech using the playsound library
playsound.playsound("output.mp3")