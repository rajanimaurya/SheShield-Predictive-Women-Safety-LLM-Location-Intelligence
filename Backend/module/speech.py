import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
from googletrans import Translator
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SpeechRecognitionEngine:
    def __init__(self):
        self.env_vars = dotenv_values(".env")
        self.input_language = self.env_vars.get("inputLanguage", "en-US")
        self.driver = None
        self.is_listening = False
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome driver for speech recognition"""
        try:
            # Create data directory
            self.data_dir = os.path.join(os.getcwd(), "Data")
            os.makedirs(self.data_dir, exist_ok=True)
            
            # HTML for speech recognition
            html_code = self.generate_html()
            html_path = os.path.join(self.data_dir, "Voice.html")
            
            with open(html_path, "w", encoding='utf-8') as f:
                f.write(html_code)
            
            # Chrome options
            chrome_options = Options()
            user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            chrome_options.add_argument(f"user-agent={user_agent}")
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            chrome_options.add_argument("--use-fake-device-for-media-stream")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Initialize driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.get(f"file://{os.path.abspath(html_path)}")
            logger.info("Speech recognition engine initialized")
            
        except Exception as e:
            logger.error(f"Driver setup error: {e}")
            raise
    
    def generate_html(self):
        """Generate HTML for speech recognition"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Speech Recognition</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        button {{
            padding: 10px 20px;
            margin: 5px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }}
        #start {{
            background: #4CAF50;
            color: white;
        }}
        #end {{
            background: #f44336;
            color: white;
        }}
        #output {{
            margin-top: 20px;
            padding: 15px;
            background: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 5px;
            min-height: 60px;
            font-size: 16px;
            line-height: 1.5;
        }}
        .status {{
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }}
        .listening {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🎤 Speech Recognition</h2>
        <div class="status" id="status">Click Start to begin listening</div>
        <button id="start">🎤 Start Listening</button>
        <button id="end">⏹️ Stop Listening</button>
        <div id="output"></div>
    </div>

    <script>
        let recognition = null;
        let isListening = false;
        
        // Initialize speech recognition
        function initSpeechRecognition() {{
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "{self.input_language}";
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = function() {{
                isListening = true;
                document.getElementById('status').innerHTML = '<strong>🔴 Listening...</strong> Speak now!';
                document.getElementById('status').className = 'status listening';
            }};

            recognition.onresult = function(event) {{
                const resultText = event.results[0][0].transcript;
                console.log("Recognized:", resultText);
                
                const output = document.getElementById('output');
                output.innerHTML = '<strong>Recognized:</strong> ' + resultText;
                
                document.getElementById('status').innerHTML = '✅ Speech recognized!';
                document.getElementById('status').className = 'status';
            }};

            recognition.onerror = function(event) {{
                console.error("Speech recognition error:", event.error);
                document.getElementById('status').innerHTML = '❌ Error: ' + event.error;
                document.getElementById('status').className = 'status';
                isListening = false;
            }};

            recognition.onend = function() {{
                isListening = false;
                document.getElementById('status').innerHTML = '⏹️ Ready to listen';
                document.getElementById('status').className = 'status';
            }};
        }}

        document.getElementById('start').onclick = function() {{
            if (!recognition) {{
                initSpeechRecognition();
            }}
            if (!isListening) {{
                recognition.start();
            }}
        }};

        document.getElementById('end').onclick = function() {{
            if (recognition && isListening) {{
                recognition.stop();
            }}
        }};

        // Initialize on load
        window.onload = function() {{
            initSpeechRecognition();
        }};
    </script>
</body>
</html>'''
    
    def SetAssistantStatus(self, status):
        """Set assistant status in file"""
        try:
            status_file = os.path.join(self.data_dir, "AssistantStatus.txt")
            with open(status_file, "w", encoding='utf-8') as f:
                f.write(status)
            logger.debug(f"Assistant status updated: {status}")
        except Exception as e:
            logger.warning(f"Could not update assistant status: {e}")
    
    def QueryModifier(self, query):
        """Modify query with proper punctuation"""
        if not query or not query.strip():
            return "No speech detected."
            
        wh_words = {"what", "when", "where", "who", "whom", "whose", "which", "why", "how"}
        new_query = query.strip()
        
        # Add punctuation if missing
        if new_query and new_query[-1] not in '.!?':
            words = new_query.split()
            if words and words[0].lower() in wh_words:
                new_query += '?'
            else:
                new_query += '.'
        
        return new_query.capitalize()
    
    def UniversalTranslator(self, text):
        """Translate text to English"""
        try:
            if not text or text == "No speech detected.":
                return text
                
            translator = Translator()
            translation = translator.translate(text, dest="en")
            return translation.text.capitalize()
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def SpeechRecognition(self, timeout=15):
        """Main speech recognition function"""
        try:
            if not self.driver:
                self.setup_driver()
            
            self.is_listening = True
            self.SetAssistantStatus("Listening...")
            
            logger.info("Starting speech recognition...")
            print("🎤 Listening... Speak now!")
            
            # Click start button
            start_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "start"))
            )
            start_button.click()
            
            start_time = time.time()
            last_text = ""
            
            while self.is_listening and (time.time() - start_time) < timeout:
                try:
                    # Get recognized text
                    output_element = self.driver.find_element(By.ID, "output")
                    current_text = output_element.text.strip()
                    
                    # Remove "Recognized:" prefix if present
                    if current_text.startswith("Recognized:"):
                        current_text = current_text.replace("Recognized:", "").strip()
                    
                    if current_text and current_text != last_text:
                        logger.info(f"Speech recognized: {current_text}")
                        print(f"✅ Recognized: {current_text}")
                        
                        # Process the text
                        if self.input_language.lower().startswith("en"):
                            final_text = self.QueryModifier(current_text)
                        else:
                            self.SetAssistantStatus("Translating...")
                            final_text = self.QueryModifier(
                                self.UniversalTranslator(current_text)
                            )
                        
                        self.SetAssistantStatus("Processing...")
                        self.is_listening = False
                        return final_text
                    
                    last_text = current_text
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.debug(f"Waiting for speech: {e}")
                    time.sleep(0.5)
            
            # Timeout or no speech detected
            if self.is_listening:
                logger.warning("Speech recognition timeout")
                print("⏰ No speech detected within timeout period")
            
            self.is_listening = False
            return "No speech detected."
            
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            self.is_listening = False
            return "No speech detected."
    
    def stop_listening(self):
        """Stop speech recognition"""
        self.is_listening = False
        try:
            if self.driver:
                stop_button = self.driver.find_element(By.ID, "end")
                stop_button.click()
        except:
            pass
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Speech recognition cleaned up")
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")

# Global instance
_speech_engine = None

def get_speech_engine():
    """Get or create speech engine instance"""
    global _speech_engine
    if _speech_engine is None:
        _speech_engine = SpeechRecognitionEngine()
    return _speech_engine

def SpeechRecognition():
    """Main function for speech recognition"""
    engine = get_speech_engine()
    return engine.SpeechRecognition()

def stop_speech_recognition():
    """Stop speech recognition"""
    global _speech_engine
    if _speech_engine:
        _speech_engine.stop_listening()

def cleanup_speech_engine():
    """Cleanup speech engine"""
    global _speech_engine
    if _speech_engine:
        _speech_engine.cleanup()
        _speech_engine = None

if __name__ == "__main__":
    print("🎤 Speech Recognition Test Mode")
    print("Speak after 'Listening...' message appears")
    print("Press Ctrl+C to exit\n")
    
    try:
        while True:
            result = SpeechRecognition()
            if result and result != "No speech detected.":
                print(f"📝 Final text: {result}")
            else:
                print("❌ No speech detected")
            
            print("\n" + "="*40 + "\n")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    finally:
        cleanup_speech_engine()