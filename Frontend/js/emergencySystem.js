// Emergency System Management
class EmergencySystem {
    constructor() {
        this.isActive = false;
        this.emergencyContacts = [];
        this.emergencyProtocols = [];
        this.initializeSystem();
    }

    initializeSystem() {
        this.loadEmergencyContacts();
        this.setupEmergencyProtocols();
        this.monitorSystemStatus();
    }

    async activateEmergency() {
        if (this.isActive) return;

        this.isActive = true;
        
        // Visual and audio alerts
        this.triggerVisualAlert();
        this.triggerAudioAlert();
        
        // Execute emergency protocols
        await this.executeEmergencyProtocols();
        
        // Notify contacts and authorities
        await this.notifyEmergencyContacts();
        await this.alertAuthorities();
        
        // Start location tracking
        this.startLocationTracking();
    }

    triggerVisualAlert() {
        document.body.style.animation = 'emergency-alert 1s infinite';
        
        // Create emergency overlay
        const overlay = document.createElement('div');
        overlay.className = 'emergency-overlay';
        overlay.innerHTML = `
            <div class="emergency-modal">
                <div class="emergency-header">
                    <i class="fas fa-bell"></i>
                    <h2>EMERGENCY SOS ACTIVATED</h2>
                </div>
                <div class="emergency-content">
                    <p>Help is on the way. Stay on the line.</p>
                    <div class="emergency-timer">00:30</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
    }

    triggerAudioAlert() {
        // Play emergency sound
        const audio = new Audio('audio/alert.mp3');
        audio.loop = true;
        audio.play().catch(e => console.log('Audio play failed:', e));
    }

    async executeEmergencyProtocols() {
        for (const protocol of this.emergencyProtocols) {
            await this.executeProtocol(protocol);
        }
    }

    async executeProtocol(protocol) {
        switch (protocol.type) {
            case 'location_share':
                await this.shareLiveLocation();
                break;
            case 'contact_notify':
                await this.notifySpecificContacts(protocol.contacts);
                break;
            case 'authority_alert':
                await this.alertSpecificAuthorities(protocol.authorities);
                break;
        }
    }

    async shareLiveLocation() {
        try {
            const position = await Utils.getLocation();
            const locationData = {
                lat: position.coords.latitude,
                lng: position.coords.longitude,
                timestamp: new Date().toISOString(),
                accuracy: position.coords.accuracy
            };
            
            // Simulate sharing location
            await Utils.simulateNetworkRequest(locationData);
            console.log('Live location shared:', locationData);
        } catch (error) {
            console.error('Location sharing failed:', error);
        }
    }

    async notifyEmergencyContacts() {
        for (const contact of this.emergencyContacts) {
            await this.sendEmergencyNotification(contact);
        }
    }

    async sendEmergencyNotification(contact) {
        const message = {
            to: contact.phone || contact.email,
            message: `🚨 EMERGENCY ALERT: ${contact.name} has activated SOS. Location: ${await this.getCurrentAddress()}`,
            priority: 'high'
        };
        
        await Utils.simulateNetworkRequest(message);
        console.log('Emergency notification sent to:', contact.name);
    }

    async alertAuthorities() {
        const authorities = [
            { name: 'Local Police', type: 'police' },
            { name: 'Emergency Services', type: 'ambulance' },
            { name: 'Security Company', type: 'security' }
        ];

        for (const authority of authorities) {
            await this.alertAuthority(authority);
        }
    }

    async alertAuthority(authority) {
        const alertData = {
            authority: authority.name,
            type: authority.type,
            location: await this.getCurrentAddress(),
            timestamp: new Date().toISOString(),
            priority: 'critical'
        };

        await Utils.simulateNetworkRequest(alertData);
        console.log('Alert sent to:', authority.name);
    }

    startLocationTracking() {
        this.locationInterval = setInterval(async () => {
            try {
                const position = await Utils.getLocation();
                this.updateEmergencyLocation(position);
            } catch (error) {
                console.error('Location tracking failed:', error);
            }
        }, 30000); // Update every 30 seconds
    }

    updateEmergencyLocation(position) {
        // Update emergency location in real-time
        const locationData = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            timestamp: new Date().toISOString()
        };
        
        console.log('Emergency location updated:', locationData);
    }

    async getCurrentAddress() {
        // Simulate reverse geocoding
        return 'Rajwada, Indore, Madhya Pradesh';
    }

    loadEmergencyContacts() {
        // Load from localStorage or default contacts
        this.emergencyContacts = JSON.parse(localStorage.getItem('emergency-contacts')) || [
            { name: 'Police', phone: '100', type: 'authority' },
            { name: 'Ambulance', phone: '108', type: 'authority' },
            { name: 'Family Member', phone: '+91XXXXXXXXXX', type: 'personal' }
        ];
    }

    setupEmergencyProtocols() {
        this.emergencyProtocols = [
            {
                type: 'location_share',
                priority: 'high',
                description: 'Share live location with emergency contacts'
            },
            {
                type: 'contact_notify',
                contacts: this.emergencyContacts.filter(c => c.type === 'personal'),
                priority: 'high',
                description: 'Notify personal emergency contacts'
            },
            {
                type: 'authority_alert',
                authorities: ['police', 'ambulance'],
                priority: 'critical',
                description: 'Alert emergency authorities'
            }
        ];
    }

    monitorSystemStatus() {
        setInterval(() => {
            this.checkSystemHealth();
        }, 60000); // Check every minute
    }

    checkSystemHealth() {
        const healthStatus = {
            gps: navigator.geolocation ? 'active' : 'inactive',
            network: navigator.onLine ? 'online' : 'offline',
            battery: this.getBatteryStatus(),
            timestamp: new Date().toISOString()
        };

        console.log('System health:', healthStatus);
    }

    getBatteryStatus() {
        // Battery status simulation
        return {
            level: 0.85,
            charging: false,
            timeRemaining: '4h 30m'
        };
    }

    deactivateEmergency() {
        this.isActive = false;
        clearInterval(this.locationInterval);
        document.body.style.animation = '';
        
        const overlay = document.querySelector('.emergency-overlay');
        if (overlay) overlay.remove();
        
        console.log('Emergency system deactivated');
    }
}

// Initialize emergency system
document.addEventListener('DOMContentLoaded', () => {
    window.emergencySystem = new EmergencySystem();
});