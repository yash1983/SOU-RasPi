#!/usr/bin/env python3
"""
SOU Raspberry Pi - Attraction B QR Scanner
Main application for Gate B ticket validation
"""

import cv2
import sys
import time
from pyzbar import pyzbar
from ticket_database import TicketDatabase
from display_manager import DisplayManager

class AttractionBScanner:
    def __init__(self):
        """Initialize Attraction B scanner"""
        self.attraction_name = "Jungle Safari"
        self.db = TicketDatabase(self.attraction_name)
        self.display = DisplayManager(self.attraction_name)
        self.camera = None
        self.running = True
        
        # Add sample tickets for testing (if enabled in config)
        self.db.add_sample_tickets_if_enabled()
        
    def initialize_camera(self):
        """Initialize USB camera"""
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            print("❌ Error: Could not open camera")
            return False
        
        # Set camera properties for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        
        print("✅ Camera initialized successfully")
        return True
    
    def scan_qr_code(self, frame):
        """Scan for QR codes in the frame"""
        try:
            qr_codes = pyzbar.decode(frame)
            if qr_codes:
                # Return the first QR code found
                return qr_codes[0].data.decode('utf-8')
        except Exception as e:
            print(f"❌ Error scanning QR code: {e}")
        
        return None
    
    def validate_ticket(self, qr_data):
        """Validate ticket and return result"""
        # Validate with database using optimized method (includes attraction checking)
        result = self.db.validate_and_log_ticket(qr_data, "B")
        
        if result['valid']:
            return {
                'valid': True,
                'reason': result['reason'],
                'ticket_info': result
            }
        else:
            return {
                'valid': False,
                'reason': result['reason'],
                'ticket_info': None
            }
    
    def process_scan(self, qr_data):
        """Process QR code scan"""
        print(f"🔍 QR Code detected: {qr_data}")
        
        # Start processing time measurement
        import time
        start_time = time.time()
        
        # Validate ticket
        validation_result = self.validate_ticket(qr_data)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Get today's scan count and database statistics
        today_scans = self.db.get_today_scans()
        db_stats = self.db.get_stats()
        
        # Update connection status
        self.display.update_connection_status()
        
        if validation_result['valid']:
            processing_ms = processing_time * 1000
            print(f"✅ {validation_result['reason']} (Processed in {processing_ms:.1f}ms)")
            # Show success screen
            success_screen = self.display.create_success_screen(
                validation_result['ticket_info'], today_scans, processing_time, db_stats
            )
            self.display.show_screen(success_screen)
            
            # Show success screen for 3 seconds
            cv2.waitKey(3000)
        else:
            processing_ms = processing_time * 1000
            print(f"❌ {validation_result['reason']} (Processed in {processing_ms:.1f}ms)")
            # Show error screen
            error_screen = self.display.create_error_screen(
                validation_result['reason'], today_scans, processing_time, db_stats
            )
            self.display.show_screen(error_screen)
            
            # Show error screen for 3 seconds
            cv2.waitKey(3000)
        
        # Mark scan time to prevent duplicate scans
        self.display.mark_scan_time()
    
    def run(self):
        """Main application loop"""
        print("=" * 60)
        print(f"🎯 SOU Raspberry Pi - {self.attraction_name} QR Scanner")
        print("=" * 60)
        
        # Initialize camera
        if not self.initialize_camera():
            return False
        
        # Setup fullscreen display
        self.display.setup_fullscreen()
        
        print("📱 Starting QR scanner...")
        print("   - Point camera at QR code to scan")
        print("   - Press 'q' to quit")
        print("   - Press 'r' to reset scan cooldown")
        print("   - Press 's' to show stats")
        
        try:
            while self.running:
                # Read camera frame
                ret, frame = self.camera.read()
                if not ret:
                    print("❌ Failed to read camera frame")
                    break
                
                # Resize frame for better performance
                frame = cv2.resize(frame, (640, 480))
                
                # Check if we can scan (cooldown period)
                if self.display.can_scan():
                    # Scan for QR codes
                    qr_data = self.scan_qr_code(frame)
                    
                    if qr_data:
                        self.process_scan(qr_data)
                        continue
                
                # Show waiting screen
                today_scans = self.db.get_today_scans()
                db_stats = self.db.get_stats()
                waiting_screen = self.display.create_waiting_screen(today_scans, db_stats=db_stats)
                self.display.show_screen(waiting_screen)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("👋 Quitting scanner...")
                    break
                elif key == ord('r'):
                    print("🔄 Reset scan cooldown")
                    self.display.last_scan_time = 0
                elif key == ord('s'):
                    stats = self.db.get_stats()
                    print(f"📊 Stats: {stats}")
        
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        finally:
            self.cleanup()
        
        return True
    
    def cleanup(self):
        """Cleanup resources"""
        if self.camera:
            self.camera.release()
        self.display.cleanup()
        print("🧹 Cleanup completed")

def main():
    """Main function"""
    scanner = AttractionBScanner()
    success = scanner.run()
    
    if success:
        print("✅ Attraction B scanner completed successfully!")
        return 0
    else:
        print("❌ Attraction B scanner failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
