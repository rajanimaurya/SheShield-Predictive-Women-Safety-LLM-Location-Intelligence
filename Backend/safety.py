import time
import os
import requests
from dotenv import load_dotenv
import asyncio
import pygame
import speech_recognition as sr
from module.text import TTS  # Import Text-to-Speech function
from module.speech import SpeechRecognition as STT  # Import Speech-to-Text function
import re

# Load API token
load_dotenv()

API_TOKEN = os.getenv("TOGETHER_API_KEY")
API_URL = "https://api.together.xyz/v1/chat/completions"

# Store previous results to avoid redundant calls
previous_queries = {}

# Log file for history
LOG_FILE = "safety_app_log.txt"

def show_welcome_message():
    print("\n Hey Girls! I'm your Safety Guard 🤖 - Any Time, Any Where! ")
    print(" Use me like this: Enter your location and time, and I'll tell you if it's safe! 🚀\n")

def log_query(location, time, response):
    with open(LOG_FILE, "a") as log:
        log.write(f"Location: {location}, Time: {time}\nResponse: {response}\n{'-'*40}\n")

def get_google_maps_link(location):
    return f"https://www.google.com/maps/search/{location.replace(' ', '+')}"

def clean_response_for_tts(response):
    """Clean the response text by removing unwanted symbols and markdown formatting."""
    # Remove markdown headers, bullet points, and emojis
    response = re.sub(r'###.*?(\n|$)', '', response)  # Remove markdown headers
    response = re.sub(r'[*`]', '', response)  # Remove emojis and asterisks
    response = re.sub(r'\n+', '\n', response)  # Clean up extra newlines
    response = re.sub(r'\s+', ' ', response)  # Remove extra spaces
    return response.strip()

def get_safety_status(location, time):
    query_key = f"{location.lower()}_{time.lower()}"
    if query_key in previous_queries:
        print(f"Previously checked: '{location}' at {time}. No change in status.\n")
        return previous_queries[query_key]
    
    # Advanced professional prompt for LLM
    prompt = f"""
    **Advanced Travel Safety Assessment Assistant**

    Aap ek smart travel safety assistant ke saath baat kar rahe ho jo aapko batayega ki kisi bhi jagah aur time pe travel karna safe hai ya nahi. 
    Assessment in cheezon pe based hoga:

    1. **Crime Trends:** Recent crime reports, purane cases, aur area mein kis type ke incidents zyada hue hain.
    2. **Situational Awareness:** Wahan ki bheed bhaad, raat mein light ka hona, aur koi local alert ya advisory.
    3. **User Intent:** Agar aap baar-baar wahi location poochh rahe ho, toh naye updates bhi bataye jayenge.

    **Response Format (Jawab ka format):**
    1.  **Risk Level:** Safe / ⚠️ Moderate Risk (thoda risk) / High Risk (zyada danger)
    2.  **Incident Insights:** Wahan pe kya dikkat ho sakti hai (jaise rape, murder, chori, ched-chad, ya koi aur crime).
    3.  **Precaution Tips:** Safe rehne ke tips, jaise kis route se jaayein, kis time travel avoid karein, aur kis transport ka use karein.
    4. **Alternative Routes:** Agar jagah risky ho toh aas-paas ka safer area suggest karein.
    5.  **Google Maps Link:** Location check karne ke liye Google Maps ka link.

    **Tone:** Simple, friendly aur helpful ho  jisse har koi aaram se samajh sake.

    **Example Output:**
    **High Risk:** Kidderpore, Kolkata raat 10 baje travel karna safe nahi hai, especially agar aap akeli ho. 
    Reports ke hisaab se yahaan rape, ladkiyon ke sath badtameezi, chori aur ched-chad jaise cases report hue hain.
    **Precautions:** Akeli mat nikliye, trusted vehicle ka use kariye, aur well-lit (roshan) areas mein hi rahiyega.
    **Suggestion:** Alipore ya Park Street jaise jagah better hain, wahan security aur camera coverage zyada hai.
     Maps: https://www.google.com/maps/search/Kidderpore+Kolkata

    **Ab is jagah ka safety assessment dein:**
    -  **Location:** {location}
    -  **Time:** {time}

    Aapka jawab clear, professional aur user-friendly hona chahiye.
    """

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "prompt": prompt,  # Use the defined prompt variable
        "max_tokens": 200,
        "temperature": 0.5,
        "top_p": 0.7,
        "repetition_penalty": 1.1,
        "stop": ["</s>"]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]

        # Add Google Maps link
        maps_link = get_google_maps_link(location)
        final_response = f"{result}\nMaps: {maps_link}"

        # Clean the response before passing it to TTS
        cleaned_response = clean_response_for_tts(final_response)

        # Store result for future reference and log it
        previous_queries[query_key] = cleaned_response
        log_query(location, time, cleaned_response)
        return cleaned_response

    except requests.exceptions.HTTPError as e:
        print(f" HTTP Error: {e}\n")
    except Exception as e:
        print(f" Failed to get a response. Error: {e}\n")
    return None

def recognize_speech():
    """Convert spoken words into text using Speech Recognition."""
    try:
        print("\nSpeak now...")
        text = STT()  # Call Speech-to-Text function
        print(f" Recognized Speech: {text}")
        return text
    except Exception as e:
        print(f"Speech Recognition Error: {e}")
        return None

# Main loop for user input
def main():
    show_welcome_message()
    while True:
        print("\n🎙️ Press 'Enter' to speak, type location manually, or type 'exit' to quit.")
        user_input = input("📍 Enter location (or press Enter to speak): ").strip()

        if user_input.lower() == 'exit':
            print("👋 Stay safe! Remember, I'm always here for you. Bye! Take care yourself  💕")
            break

        location = user_input if user_input else recognize_speech()

        if not location:
            print("⚠️ No location detected. Try again.")
            continue

        time_of_travel = input(" Enter time (or press Enter to speak): ").strip()
        if not time_of_travel:
            time_of_travel = recognize_speech()

        if not time_of_travel:
            print("⚠️ No time detected. Try again.")
            continue

        print("\n🔍 Checking safety status... Please wait...\n")
        safety_response = get_safety_status(location, time_of_travel)

        if safety_response:
            if "red alert" in safety_response.lower() or "" in safety_response:
                print(f" EMERGENCY ALERT: {safety_response}\n")
            else:
                print(f" {safety_response}\n")

            # Convert safety response into speech
            print(" Reading safety response...")
            TTS(safety_response)
        else:
            print("⚠️ Could not determine the safety status. Please try again later.\n")

if __name__ == "__main__":
    main()
