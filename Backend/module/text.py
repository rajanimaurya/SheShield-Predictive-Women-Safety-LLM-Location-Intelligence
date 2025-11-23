import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

if not AssistantVoice:
    raise ValueError("❌ Error: AssistantVoice not found in .env file.")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

async def TextToSpeech(text) -> None:
    file_path = "data/speech.mp3"
    
    if os.path.exists(file_path):
        os.remove(file_path)
        
    communication = edge_tts.Communicate(text, AssistantVoice,  rate='+13%') 

    await communication.save(file_path)

def TTS(Text, func=lambda r=None: True):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(TextToSpeech(Text))
        
        pygame.mixer.init()
        
        if not os.path.exists("data/speech.mp3"):
            print("❌ Error: speech file not found.")
            return False
        
        pygame.mixer.music.load("data/speech.mp3")
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            if func() is False:
                break
            pygame.time.Clock().tick(10)
        
        return True
    
    except Exception as e:
        print("❌ Error in TTS:", e)
    
    finally:
        try:
            func(False)
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception as e:
            print(f"❌ Error in finally block: {e}")

def TesToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")
   
   
    responses = [
    "Ma'am, the remaining part of the result, along with a detailed explanation and relevant insights, has been printed on the chat screen. Please check it out for a complete understanding.",
    "Ma'am, the continuation of the answer, including key points, examples, and additional explanations, is now visible on the chat screen. Kindly take a look to get a clear perspective.",
    "You can find the rest of the text, along with further elaboration on the topic, important context, and supporting details, displayed on the chat screen, ma'am.",
    "The remaining part of the text, along with essential clarifications and additional insights to enhance comprehension, has been posted on the chat screen, ma'am.",
    "Ma'am, I have shared the next portion of the answer on the chat screen, ensuring that it includes relevant details, examples, and necessary explanations for better understanding.",
    "The rest of the answer, with important points, clarifications, and a structured breakdown of the topic, is now available on the chat screen, ma'am.",
    "Ma'am, please check the chat screen for the complete response, which includes in-depth explanations, supporting details, and additional context to provide a thorough understanding.",
    "You'll find the detailed continuation of the answer, enriched with key insights, structured information, and relevant examples, on the chat screen, ma'am.",
    "The next section of the text, which contains a deeper discussion on the topic, additional references, and useful explanations, is now available on the chat screen, ma'am."
]
 
    #  Added a default response to avoid errors.
    
    if len(Data) > 4 and len(Text) >= 250:
        TTS("".join(Text.split(".")[0:2]) + "." + random.choice(responses), func)
    else:
        TTS(Text, func)

if __name__ == "__main__":
    while True:
        text = input("Enter the text (or type 'exit' to quit): ")
        if text.lower() == "exit":
            print("Exiting...")
            break
        TesToSpeech(text)
        
        
        
