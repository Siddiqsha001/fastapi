from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
import cv2
import speech_recognition as sr
from deep_translator import GoogleTranslator
import threading
import time
import io

app = FastAPI()

# Initialize speech recognizer and camera
recognizer = sr.Recognizer()
cap = cv2.VideoCapture(0)
translated_text = "Listening..."
source_lang = "en"
target_lang = "ta"

# Function to continuously recognize and translate speech
def recognize_and_translate():
    global translated_text
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print(f"Listening in {source_lang}... (Speak anytime)")
            try:
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

# Start the translation thread
translation_thread = threading.Thread(target=recognize_and_translate, daemon=True)
translation_thread.start()

# API to set language preferences
@app.post("/set_languages/")
def set_languages(source: str, target: str):
    global source_lang, target_lang
    source_lang = source
    target_lang = target
    return {"message": f"Language set from {source_lang} to {target_lang}"}

# API to get the translated text
@app.get("/get_translation/")
def get_translation():
    return {"translated_text": translated_text}

# Video streaming generator
def generate_video():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Display translated text on the video frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_position = (50, frame.shape[0] - 50)
        font_scale = 1
        font_color = (0, 255, 0)  # Green
        thickness = 2

        cv2.putText(frame, translated_text, text_position, font, font_scale, font_color, thickness, cv2.LINE_AA)

        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()
        
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

# API to stream video with translation
@app.get("/video_feed/")
def video_feed():
    return StreamingResponse(generate_video(), media_type="multipart/x-mixed-replace; boundary=frame")

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
