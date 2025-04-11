import os
import sys
import requests
from pynput import keyboard
from PIL import ImageGrab, Image
import google.generativeai as genai

GOOGLE_API_KEY = "REPLACE_WITH_YOUR_GOOGLE_API"
GEMINI_MODEL_ID = "gemini-2.0-flash"

VERSION = '1.0.4'

def check_version():
    response = requests.get("https://raw.githubusercontent.com/Orbinuity/MathAI/main/latest.version")

    if response.status_code == 200:
        latestVersion = response.text
    else:
        print(f"Failed to retrieve data: {response.status_code}, maby you wifi is off?")
        sys.exit(1)

    if VERSION != latestVersion:
        print(f"New version available: {latestVersion}, please update!")
        sys.exit(1)
    
check_version()
print("Update check complete, you are on the latest version!")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(GEMINI_MODEL_ID)

def send_notification(title, message):
    print(f"{title} - {message}")
    command = f'notify-send "{title}" "{message}"'
    os.system(command)

def screenshot(name):
    screenshot = ImageGrab.grab()
    screenshot.save(name)
    return name

def null(key): pass

def analyze_image(image_path):
    try:
        img = Image.open(image_path)
        response = model.generate_content(["On this image is a math problem if not say ONLY 'error 1'(with out ') if there is 1 awnser needed(example): 13 and if for examople 2: 15, 94 and if its with remainder(for example)(AND IF THERE IS NO remainder DONT DO IT WITH remainder JUST NORMAL DEVIDE BY!!!!): 12 remainder: 2. and if its 2 times with remainder(for example): 12 remainder: 2, 15 remainder: 3, NEVER USE ENTER DO IT EXACTLY LIKE I SHOWED HERE!!!", img])
        response.resolve()
        if response.text == "error 1":
            return "Error!", "No math problem found!"
        else:
            os.system(f"""python win.py "{response.text}" > /dev/null 2>&1 &""")
            return "Awnser(s) Found!", response.text
    except Exception as e:
        return "Error!", f"Error analyzing image: {str(e)}!"

def on_press(key):
    if key == keyboard.Key.f8:
        check_version()
        print("You pressed 'f8'!")
        shot_name = screenshot("screenshot.png")
        
        if os.path.exists(shot_name):
            send_notification("Loading...", "Letting the magic happen!")
            title, desc = analyze_image(shot_name)
            send_notification(title, desc)
        else:
            print(f"Image file not found: {shot_name}")

with keyboard.Listener(on_press=on_press, on_release=null) as listener:
    listener.join()