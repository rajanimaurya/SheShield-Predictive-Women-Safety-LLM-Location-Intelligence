import os
import threading
import datetime
import requests
import time
import speech_recognition as sr
from twilio.rest import Client
from dotenv import load_dotenv
import pygame
import logging
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SOSEmergencySystem:
    def __init__(self):
        load_dotenv()
        
        # Twilio credentials
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Emergency contacts
        contacts = os.getenv('EMERGENCY_CONTACTS', '')
        self.emergency_contacts = [c.strip() for c in contacts.split(',') if c.strip()]
        
        # File paths
        self.base_dir = Path(__file__).parent.parent
        self.alert_sound_path = self.base_dir / "data" / "alert.mp3"
        self.fake_call_path = self.base_dir / "data" / "fake_call.mp3"
        self.log_file_path = self.base_dir / "Files" / "sos.log"
        
        # Ensure directories exist
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.alert_sound_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file
        self._init_log_file()
        
        # System state
        self.sos_active = False
        self.voice_listener_active = False
        
        logger.info("SOS Emergency System initialized")
    
    def _init_log_file(self):
        """Initialize log file"""
        try:
            if not self.log_file_path.exists():
                with open(self.log_file_path, 'w') as f:
                    f.write("SOS Emergency System Log\n")
                    f.write("=" * 50 + "\n")
        except Exception as e:
            logger.error(f"Log file initialization error: {e}")
    
    def log_event(self, message):
        """Log event with timestamp"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            with open(self.log_file_path, 'a') as log_file:
                log_file.write(log_entry)
            
            logger.info(message)
        except Exception as e:
            logger.error(f"Logging error: {e}")
    
    def get_location(self):
        """Get current location using IP geolocation"""
        try:
            response = requests.get("https://ipinfo.io/json", timeout=10)
            data = response.json()
            
            loc = data.get('loc', 'Unknown')
            city = data.get('city', 'Unknown')
            country = data.get('country', 'Unknown')
            
            location_info = {
                'coordinates': loc,
                'city': city,
                'country': country,
                'maps_url': f"https://www.google.com/maps?q={loc}",
                'full_address': f"{city}, {country}"
            }
            
            logger.info(f"Location retrieved: {location_info['full_address']}")
            return location_info
            
        except Exception as e:
            logger.error(f"Location error: {e}")
            return {
                'coordinates': 'Unknown',
                'city': 'Unknown', 
                'country': 'Unknown',
                'maps_url': 'Location unavailable',
                'full_address': 'Location unavailable'
            }
    
    def play_alert_sound(self, sound_path):
        """Play alert sound continuously"""
        try:
            if not sound_path.exists():
                logger.warning(f"Alert sound file not found: {sound_path}")
                return
            
            pygame.mixer.init()
            pygame.mixer.music.load(str(sound_path))
            pygame.mixer.music.play(-1)  # Loop indefinitely
            logger.info("Alert sound started")
            
        except Exception as e:
            logger.error(f"Alert sound error: {e}")
    
    def stop_alert_sound(self):
        """Stop alert sound"""
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            logger.info("Alert sound stopped")
        except Exception as e:
            logger.warning(f"Error stopping alert sound: {e}")
    
    def send_sms(self, contact, message):
        """Send emergency SMS"""
        if contact == self.twilio_number:
            return False
            
        try:
            client = Client(self.account_sid, self.auth_token)
            message = client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=contact
            )
            self.log_event(f"SMS sent to {contact} - SID: {message.sid}")
            return True
            
        except Exception as e:
            self.log_event(f"SMS failed to {contact}: {str(e)}")
            return False
    
    def make_call(self, contact, voice_message):
        """Make emergency call"""
        if contact == self.twilio_number:
            return False
            
        try:
            client = Client(self.account_sid, self.auth_token)
            call = client.calls.create(
                twiml=f'<Response><Say voice="alice">{voice_message}</Say></Response>',
                from_=self.twilio_number,
                to=contact
            )
            self.log_event(f"Call initiated to {contact} - SID: {call.sid}")
            return True
            
        except Exception as e:
            self.log_event(f"Call failed to {contact}: {str(e)}")
            return False
    
    def emergency_auto_call(self):
        """Make automatic emergency call after delay"""
        if not self.sos_active:
            return
            
        time.sleep(30)  # Wait 30 seconds
        
        if self.sos_active:  # Double-check SOS is still active
            logger.info("No response detected, making automatic emergency call")
            self.make_call(
                self.emergency_contacts[0] if self.emergency_contacts else "+911",  # Emergency number
                "Emergency! No response from user. Immediate assistance required."
            )
    
    def listen_for_sos_voice(self):
        """Listen for voice activation"""
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
        
        self.voice_listener_active = True
        logger.info("Voice activation listener started")
        
        while self.voice_listener_active:
            try:
                with microphone as source:
                    print("🎤 Listening for 'help me'...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                
                command = recognizer.recognize_google(audio).strip().lower()
                logger.debug(f"Voice command heard: {command}")
                
                if "help me" in command or "emergency" in command or "sos" in command:
                    logger.info("SOS activated by voice command")
                    self.activate_sos()
                    break
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                logger.error(f"Speech recognition error: {e}")
                break
            except Exception as e:
                logger.error(f"Voice listener error: {e}")
                break
    
    def activate_sos(self):
        """Activate SOS emergency system"""
        if self.sos_active:
            logger.warning("SOS already active")
            return
        
        self.sos_active = True
        self.log_event("🚨 SOS EMERGENCY ACTIVATED")
        
        print("🚨 EMERGENCY SOS ACTIVATED!")
        print("🆘 Notifying emergency contacts...")
        
        # Get location
        location_info = self.get_location()
        
        # Create messages
        sms_message = f"""🚨 EMERGENCY ALERT 🚨

I am in danger and need immediate help!

📍 Location: {location_info['full_address']}
🗺️ Maps: {location_info['maps_url']}
📱 Coordinates: {location_info['coordinates']}

🆘 Please send help immediately!

Sent via Girlas Safety App"""

        voice_message = f"""Emergency! I am in danger and need immediate assistance. 
        My location is {location_info['city']}, {location_info['country']}. 
        Please send help immediately."""
        
        # Start alert sound
        sound_thread = threading.Thread(
            target=self.play_alert_sound, 
            args=(self.alert_sound_path,)
        )
        sound_thread.daemon = True
        sound_thread.start()
        
        # Send notifications to all contacts
        notification_threads = []
        
        for contact in self.emergency_contacts:
            if contact:
                # SMS thread
                sms_thread = threading.Thread(
                    target=self.send_sms,
                    args=(contact, sms_message)
                )
                sms_thread.daemon = True
                sms_thread.start()
                notification_threads.append(sms_thread)
                
                # Call thread
                call_thread = threading.Thread(
                    target=self.make_call,
                    args=(contact, voice_message)
                )
                call_thread.daemon = True
                call_thread.start()
                notification_threads.append(call_thread)
        
        # Start auto emergency call
        auto_call_thread = threading.Thread(target=self.emergency_auto_call)
        auto_call_thread.daemon = True
        auto_call_thread.start()
        
        logger.info(f"SOS activated for {len(self.emergency_contacts)} contacts")
        
        # Wait for notifications to complete
        for thread in notification_threads:
            thread.join(timeout=10)
    
    def deactivate_sos(self):
        """Deactivate SOS system"""
        self.sos_active = False
        self.voice_listener_active = False
        self.stop_alert_sound()
        self.log_event("SOS system deactivated")
        logger.info("SOS system deactivated")
    
    def start_voice_listener(self):
        """Start voice activation listener"""
        voice_thread = threading.Thread(target=self.listen_for_sos_voice)
        voice_thread.daemon = True
        voice_thread.start()
        return voice_thread

# Global instance
_sos_system = None

def get_sos_system():
    """Get or create SOS system instance"""
    global _sos_system
    if _sos_system is None:
        _sos_system = SOSEmergencySystem()
    return _sos_system

def activate_sos():
    """Activate SOS emergency system"""
    system = get_sos_system()
    system.activate_sos()

def start_voice_activation():
    """Start voice activation for SOS"""
    system = get_sos_system()
    return system.start_voice_listener()

def deactivate_sos():
    """Deactivate SOS system"""
    global _sos_system
    if _sos_system:
        _sos_system.deactivate_sos()

if __name__ == "__main__":
    print("🆘 SOS Emergency System")
    print("Starting voice activation listener...")
    print("Say 'help me' to activate SOS")
    print("Press Ctrl+C to exit\n")
    
    try:
        system = get_sos_system()
        voice_thread = system.start_voice_listener()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down SOS system...")
        deactivate_sos()