# notification.py (FREE VERSION - CORRECTED)
import os
import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import datetime
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationSystem:
    def __init__(self):
        load_dotenv()
        
        # Only email credentials needed
        self.sender_email = os.getenv('GMAIL_EMAIL')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD')
        
        # Emergency contacts
        self.emergency_contacts = [
            {"email": "rajanimauryalu09@gmail.com", "name": "Rajani"},
            {"email": "annumauryalu01@gmail.com", "name": "Annu"},
        ]
        
        self.last_sent_time = 0
        self.min_interval = 60
        
        logger.info("FREE SOS Notification system initialized")

    def get_precise_location_from_mobile(self, lat, lon):
        """FREE version - No Google Maps API needed"""
        try:
            logger.info("Using MOBILE GPS: %s, %s", lat, lon)
            
            # Direct Google Maps link without API
            google_maps_url = f"https://www.google.com/maps?q={lat},{lon}&z=16"
            
            # Get approximate address using free OpenStreetMap
            precise_address = f"📍 Exact Location: {lat:.6f}, {lon:.6f}"
            
            try:
                # FREE geocoding using OpenStreetMap
                osm_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18"
                response = requests.get(osm_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'display_name' in data:
                        precise_address = data['display_name']
                        logger.info("OpenStreetMap geocoding successful")
            except Exception as e:
                logger.warning("OpenStreetMap failed: %s", e)
                # If free service fails, use coordinates

            return {
                "precise_address": precise_address,
                "coordinates": f"{lat:.6f},{lon:.6f}",
                "latitude": lat,
                "longitude": lon,
                "google_maps_url": google_maps_url,
                "source": "mobile_gps_free"
            }

        except Exception as e:
            logger.error("Location error: %s", e)
            return {
                "precise_address": f"Coordinates: {lat}, {lon}",
                "coordinates": f"{lat},{lon}",
                "google_maps_url": f"https://www.google.com/maps?q={lat},{lon}",
                "source": "mobile_gps"
            }

    def _send_sos_email(self, to_email, recipient_name, location_data, timestamp, extra_info=None):
        """Send SOS email - FREE version"""
        try:
            subject = "🚨 SOS EMERGENCY - LIVE LOCATION 🚨"
            
            body = f"""
URGENT SOS ALERT! 🚨

Hello {recipient_name},

🚨 EMERGENCY ALERT from Girls Safety App

👤 PERSON IN DANGER:
• Name: Rajani Maurya
• Phone: +91 8318629910
• Time: {timestamp}

📍 LIVE LOCATION:
{location_data.get('precise_address')}

🗺️ GOOGLE MAPS (Click to Open):
{location_data.get('google_maps_url')}

📞 IMMEDIATE ACTION:
1. CALL: +91 8318629910
2. OPEN MAP LINK for exact location
3. CONTACT local police if needed
4. ALERT other contacts

{f'Additional Info: {extra_info}' if extra_info else ''}

This is an automated SOS alert. Please respond immediately.

Stay Safe,
Girls Safety App
"""
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg.attach(MIMEText(body, 'plain'))

            if not self.sender_email or not self.sender_password:
                return False

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
                smtp.login(self.sender_email, self.sender_password)
                smtp.send_message(msg)

            logger.info("FREE SOS email sent to %s", to_email)
            return True

        except Exception as e:
            logger.error("Email failed for %s: %s", to_email, e)
            return False

    def send_sos_alert_from_mobile(self, lat, lon, extra_info=None):
        """Main SOS method - FREE"""
        try:
            current_time = time.time()
            if current_time - self.last_sent_time < self.min_interval:
                return {"success": False, "error": "Please wait 60 seconds between alerts"}
            
            self.last_sent_time = current_time
            
            location_data = self.get_precise_location_from_mobile(lat, lon)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            sent_count = 0
            for contact in self.emergency_contacts:
                if self._send_sos_email(contact["email"], contact["name"], location_data, timestamp, extra_info):
                    sent_count += 1

            result = {
                "success": sent_count > 0,
                "alerts_sent": sent_count,
                "maps_link": location_data.get("google_maps_url"),
                "address": location_data.get("precise_address"),
                "timestamp": timestamp
            }
            
            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

# Global instance
_sos_system = None

def get_sos_system():
    global _sos_system
    if _sos_system is None:
        _sos_system = NotificationSystem()
    return _sos_system

# Test function
def test_sos_system():
    sos_system = NotificationSystem()
    result = sos_system.send_sos_alert_from_mobile(
        lat=28.6328, 
        lon=77.2197,
        extra_info="Testing FREE SOS system"
    )
    print("SOS Result:", result)

if __name__ == "__main__":
    test_sos_system()