import cv2
import speech_recognition as sr
from deep_translator import GoogleTranslator
import threading
import time

# Function to get user input for languages
def get_language_choice():
    print("Available Languages: English (en), Tamil (ta-IN), Hindi (hi-IN), Spanish (es), French (fr), etc.")
    source_lang = input("Enter source language code (e.g., hi-IN for Hindi, ta-IN for Tamil, en for English): ").strip()
    target_lang = input("Enter target language code (e.g., en for English, ta for Tamil, hi for Hindi): ").strip()
    return source_lang, target_lang

# Get language choices
source_lang, target_lang = get_language_choice()
print(f"Translating from {source_lang} to {target_lang}...")

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Initialize camera
cap = cv2.VideoCapture(0)

# Shared variable for translated text
translated_text = "Listening..."

def recognize_and_translate():
    global translated_text
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print(f"Listening in {source_lang}... (Speak anytime)")
            try:
                # This keeps waiting until you speak
                audio = recognizer.listen(source, timeout=None)  
                text = recognizer.recognize_google(audio, language=source_lang)
                print(f"Original ({source_lang}): {text}")

                translated_text = GoogleTranslator(source=source_lang[:2], target=target_lang).translate(text)
                print(f"Translated ({target_lang}): {translated_text}")

            except sr.UnknownValueError:
                translated_text = "Could not understand"
            except sr.RequestError:
                translated_text = "Speech Recognition error"
            time.sleep(0.5)  

# Run speech recognition in a separate thread
thread = threading.Thread(target=recognize_and_translate, daemon=True)
thread.start()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Display translated text at the bottom
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_position = (50, frame.shape[0] - 50)
    font_scale = 1
    font_color = (0, 255, 0)  # Green
    thickness = 2

    cv2.putText(frame, translated_text, text_position, font, font_scale, font_color, thickness, cv2.LINE_AA)

    # Show video
    cv2.imshow("Live Translation", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()