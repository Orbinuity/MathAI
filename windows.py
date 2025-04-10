import os
from pynput import keyboard
import google.generativeai as genai
from PIL import ImageGrab, Image
from winotify import Notification, audio
import ctypes

GOOGLE_API_KEY = "REPLACE_WITH_YOUR_GOOGLE_API"
GEMINI_MODEL_ID = "gemini-2.0-flash"

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(GEMINI_MODEL_ID)

def fallback_popup(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 1)

def send_notification(title, message):
    print(f"{title} - {message}")
    try:
        toast = Notification(
            app_id="Math AI",
            title=title,
            msg=message,
            icon=os.path.abspath("icon.png")
        )
        toast.set_audio(audio.Reminder, loop=False)
        toast.show()
    except Exception as e:
        print(f"Toast failed with: {e}, falling back to message box")
        fallback_popup(title, message)

def screenshot(name):
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(name)
        return name
    except Exception as e:
        print(f"Screenshot failed: {e}")
        return None

def null(key): pass

def analyze_image(image_path):
    try:
        img = Image.open(image_path)
        response = model.generate_content(["On this image is a math problem if not say ONLY 'error 1'(with out ') if there is say it as a python list so 1 awnser needed(example): 13 and if for examople 2: 15, 94 and if its with remainder: 12 remainder: 2. and if its 2 with remainder: 12 remainder: 2, 15 remainder: 3,", img])
        response.resolve()
        if response.text == "error 1":
            return "Error!", "No math problem found!"
        else:
            return "Awnsers Found!", response.text
    except Exception as e:
        return "Error!", f"Error analyzing image: {str(e)}"

def on_press(key):
    if key == keyboard.Key.f8:
        print("You pressed 'f8'!")
        shot_name = screenshot("screenshot.png")

        if shot_name and os.path.exists(shot_name):
            send_notification("Loading...", "Letting the magic happen...")
            title, desc = analyze_image(shot_name)
            send_notification(title, desc)
        else:
            print(f"Screenshot failed or file not found: {shot_name}")

with keyboard.Listener(on_press=on_press, on_release=null) as listener:
    listener.join()
