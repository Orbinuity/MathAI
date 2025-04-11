import os
import sys
import ctypes
import requests
from pynput import keyboard
from PIL import ImageGrab, Image
import google.generativeai as genai
from winotify import Notification, audio

GOOGLE_API_KEY = "REPLACE_WITH_YOUR_GOOGLE_API"
GEMINI_MODEL_ID = "gemini-2.0-flash"

VERSION = '1.1.1'

def check_version():
    response = requests.get("https://raw.githubusercontent.com/Orbinuity/MathAI/main/latest.version")

    if response.status_code == 200:
        latestVersion = response.text
    else:
        send_notification("Error!", f"Failed to retrieve data: {response.status_code}, maby you wifi is off?")
        print(f"Failed to retrieve data: {response.status_code}, maby you wifi is off?")
        sys.exit(1)

    if VERSION != latestVersion:
        send_notification("Update Available!", f"New version available: {latestVersion}, please update!")
        print(f"New version available: {latestVersion}, please update!")
        sys.exit(1)
    
check_version()
print("Update check complete, you are on the latest version!")

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
        response = model.generate_content(["On this image is a math problem if not say ONLY 'error 1'(with out ') if there simply just say the awnser thats it(can also be multipel awnsers)", img])
        response.resolve()
        if response.text == "error 1":
            return "Error!", "No math problem found!"
        else:
            os.system(f"""start /B python win.py "{response.text}" > null 2>&1""")
            return "Awnser(s) Found!", response.text
    except Exception as e:
        return "Error!", f"Error analyzing image: {str(e)}"

def on_press(key):
    if key == keyboard.Key.f8:
        check_version()
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
