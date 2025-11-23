# main.py
import time
import os
import threading
from dotenv import load_dotenv
import pygame

# Import all modules
from safety import get_safety_status, show_welcome_message, recognize_speech
from module.sos import get_sos_system, activate_sos, start_voice_activation, deactivate_sos
from module.text import TTS
from module.notification import get_sos_system as get_notification_system

# Load environment variables
load_dotenv()

class SafetyApp:
    def __init__(self):
        self.running = True
        self.sos_system = get_sos_system()
        self.notification_system = get_notification_system()
        
        # Initialize pygame for audio
        pygame.mixer.init()
        
        print("🚺 Girls Safety App Initialized")
        print("=" * 50)
    
    def show_main_menu(self):
        """Display the main menu options"""
        print("\n" + "=" * 50)
        print("🚺 GIRLS SAFETY APP - MAIN MENU")
        print("=" * 50)
        print("1. 🔍 Check Location Safety")
        print("2. 🆘 Activate SOS Emergency")
        print("3. 🎤 Voice-activated SOS (Background)")
        print("4. 📱 Send SOS with Location")
        print("5. 📜 View Safety History")
        print("6. 🚪 Exit")
        print("-" * 50)
    
    def check_location_safety(self):
        """Option 1: Check location safety"""
        show_welcome_message()
        
        print("\n📍 SAFETY CHECK")
        print("-" * 30)
        
        location = input("Enter location (or press Enter to speak): ").strip()
        if not location:
            location = recognize_speech()
            if not location:
                print("❌ No location detected. Returning to menu.")
                return

        time_of_travel = input("Enter time (or press Enter to speak): ").strip()
        if not time_of_travel:
            time_of_travel = recognize_speech()
            if not time_of_travel:
                print("❌ No time detected. Returning to menu.")
                return

        print("\n🔍 Checking safety status...")
        safety_response = get_safety_status(location, time_of_travel)

        if safety_response:
            print(f"\n✅ Safety Report:")
            print("-" * 40)
            print(safety_response)
            print("-" * 40)
            
            # Convert to speech
            print("🔊 Reading safety response...")
            TTS(safety_response)
        else:
            print("❌ Could not determine safety status. Please try again.")
    
    def activate_sos_emergency(self):
        """Option 2: Activate SOS emergency"""
        print("\n🚨 SOS EMERGENCY ACTIVATION")
        print("-" * 35)
        print("This will:")
        print("• Notify all emergency contacts")
        print("• Send your location via SMS/Email")
        print("• Make emergency calls")
        print("• Play alert sound")
        
        confirm = input("\nAre you sure you want to activate SOS? (yes/no): ").strip().lower()
        if confirm in ['yes', 'y']:
            print("🆘 ACTIVATING SOS EMERGENCY SYSTEM...")
            activate_sos()
        else:
            print("❌ SOS activation cancelled.")
    
    def start_voice_sos(self):
        """Option 3: Start voice-activated SOS in background"""
        print("\n🎤 VOICE-ACTIVATED SOS")
        print("-" * 30)
        print("Voice activation started in background...")
        print("Say 'help me', 'emergency', or 'SOS' to activate")
        print("This will run until you stop it from main menu")
        
        try:
            voice_thread = start_voice_activation()
            print("✅ Voice listener started in background")
            input("Press Enter to return to menu (voice listening continues)...")
        except Exception as e:
            print(f"❌ Error starting voice activation: {e}")
    
    def send_sos_with_location(self):
        """Option 4: Send SOS with precise location"""
        print("\n📱 SOS WITH LOCATION")
        print("-" * 25)
        print("Enter your current coordinates:")
        
        try:
            lat = float(input("Latitude (e.g., 28.6129): ").strip())
            lon = float(input("Longitude (e.g., 77.2295): ").strip())
            extra_info = input("Additional info (optional): ").strip()
            
            print("\n📡 Sending SOS alert with location...")
            result = self.notification_system.send_sos_alert_from_mobile(lat, lon, extra_info)
            
            if result.get("success"):
                print("✅ SOS alerts sent successfully!")
                print(f"📍 Location: {result.get('address')}")
                print(f"🗺️ Maps: {result.get('maps_link')}")
                print(f"📨 Alerts sent: {result.get('alerts_sent')}")
            else:
                print(f"❌ Failed to send alerts: {result.get('error')}")
                
        except ValueError:
            print("❌ Invalid coordinates. Please enter numeric values.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def view_safety_history(self):
        """Option 5: View safety check history"""
        print("\n📜 SAFETY CHECK HISTORY")
        print("-" * 30)
        
        log_files = [
            "safety_app_log.txt",
            "Files/sos.log",
            "safety_app_log.json"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                print(f"\n📄 {log_file}:")
                print("-" * 20)
                try:
                    with open(log_file, 'r') as f:
                        content = f.read()
                        if content:
                            print(content[:500] + "..." if len(content) > 500 else content)
                        else:
                            print("No entries yet.")
                except Exception as e:
                    print(f"Error reading {log_file}: {e}")
            else:
                print(f"📄 {log_file}: File not found")
    
    def exit_app(self):
        """Option 6: Exit the application"""
        print("\n👋 Thank you for using Girls Safety App!")
        print("Stay safe! 💕")
        self.running = False
        deactivate_sos()
        
        # Clean up pygame
        if pygame.mixer.get_init():
            pygame.mixer.quit()
    
    def run(self):
        """Main application loop"""
        print("🚺 Welcome to Girls Safety App!")
        print("Your safety companion - Any Time, Any Where! 🤖")
        
        while self.running:
            self.show_main_menu()
            
            try:
                choice = input("\nEnter your choice (1-6): ").strip()
                
                if choice == '1':
                    self.check_location_safety()
                elif choice == '2':
                    self.activate_sos_emergency()
                elif choice == '3':
                    self.start_voice_sos()
                elif choice == '4':
                    self.send_sos_with_location()
                elif choice == '5':
                    self.view_safety_history()
                elif choice == '6':
                    self.exit_app()
                else:
                    print("❌ Invalid choice. Please enter 1-6.")
                    
                # Small delay for better UX
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user")
                self.exit_app()
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                print("Returning to main menu...")
                time.sleep(2)

def main():
    """Main function to run the safety app"""
    try:
        app = SafetyApp()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start Safety App: {e}")
        print("Please check your dependencies and try again.")

if __name__ == "__main__":
    main()