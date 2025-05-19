import os
import sys
import requests
from pynput import keyboard
from PIL import ImageGrab, Image
import google.generativeai as genai

GOOGLE_API_KEY = open("api_key", 'r').read().strip()

if not GOOGLE_API_KEY:
    print("API key is empty, please fill in the api_key file!")
    sys.exit(1)

if len(sys.argv) > 1 and sys.argv[1] == "-update":
    print("Updating...")
    os.system('bash update.sh &')
    exit(0)

GEMINI_MODEL_ID = "gemini-2.0-flash"

VERSION = '1.2.1'

if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

def send_notification(title, message):
    print(f"{title} - {message}")
    command = f'notify-send "{title}" "{message}"'
    os.system(command)


def check_version():
    response = requests.get("https://raw.githubusercontent.com/Orbinuity/MathAI/main/latest.version")

    if response.status_code == 200:
        latestVersion = response.text
    else:
        send_notification("Error!", f"Failed to retrieve data: {response.status_code}, maby you wifi is off?")
        print(f"Failed to retrieve data: {response.status_code}, maby you wifi is off?")
        sys.exit(1)

    if VERSION != latestVersion:
        send_notification("Update Available!", f"New version available: {latestVersion}, please update with 'python {sys.argv[0]} -update'!")
        print(f"New version available: {latestVersion}, please update!")
        sys.exit(1)
    
check_version()
print("Update check complete, you are on the latest version!")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(GEMINI_MODEL_ID)

def screenshot(name):
    screenshot = ImageGrab.grab()
    screenshot.save(name)
    return name

def null(key): pass

def analyze_image(image_path):
    try:
        img = Image.open(image_path)
        response = model.generate_content(["On this image is a school(like math or dutch or english and more!) problem if not say ONLY 'error 1'(with out ') if there simply just say the awnser thats it(can also be multipel awnsers)", img])
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