#!/usr/bin/env python3
"""
Display Manager for SOU Raspberry Pi
Handles fullscreen display with QR scanning interface
"""

import cv2
import numpy as np
import time
import requests
from datetime import datetime

class DisplayManager:
    def __init__(self, attraction_name):
        """Initialize display manager"""
        self.attraction_name = attraction_name
        self.window_name = f"SOU {attraction_name} - QR Scanner"
        self.is_online = self.check_internet_connection()
        self.last_scan_time = 0
        self.scan_cooldown = 3.0  # 3 seconds cooldown
        
    def check_internet_connection(self):
        """Check if device is online"""
        try:
            requests.get("http://www.google.com", timeout=3)
            return True
        except:
            return False
    
    def create_waiting_screen(self, today_scans=0):
        """Create waiting screen with QR code message"""
        # Create black background
        screen = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Add attraction name
        cv2.putText(screen, f"SOU {self.attraction_name}", (640, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        cv2.putText(screen, f"SOU {self.attraction_name}", (640, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 150, 255), 2)
        
        # Add main message
        cv2.putText(screen, "Waiting for QR code...", (640, 300), 
                   cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 4)
        cv2.putText(screen, "Waiting for QR code...", (640, 300), 
                   cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 255), 3)
        
        # Add QR code icon (simplified)
        self.draw_qr_icon(screen, 640, 450)
        
        # Add status information
        self.add_status_info(screen, today_scans)
        
        return screen
    
    def create_success_screen(self, ticket_info, today_scans):
        """Create success screen with green tick"""
        screen = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Add attraction name
        cv2.putText(screen, f"SOU {self.attraction_name}", (640, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        cv2.putText(screen, f"SOU {self.attraction_name}", (640, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 150, 255), 2)
        
        # Draw green tick mark
        self.draw_tick_mark(screen, 640, 300, color=(0, 255, 0))
        
        # Add success message
        cv2.putText(screen, "Valid Entry", (640, 450), 
                   cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 4)
        
        # Add ticket info
        if ticket_info:
            info_text = f"Entries: {ticket_info['persons_entered']}/{ticket_info['persons_allowed']}"
            cv2.putText(screen, info_text, (640, 520), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        
        # Add status information
        self.add_status_info(screen, today_scans)
        
        return screen
    
    def create_error_screen(self, reason, today_scans):
        """Create error screen with red X"""
        screen = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Add attraction name
        cv2.putText(screen, f"SOU {self.attraction_name}", (640, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        cv2.putText(screen, f"SOU {self.attraction_name}", (640, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 150, 255), 2)
        
        # Draw red X mark
        self.draw_x_mark(screen, 640, 300, color=(0, 0, 255))
        
        # Add error message
        cv2.putText(screen, "Entry Not Valid", (640, 450), 
                   cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 4)
        
        # Add reason
        cv2.putText(screen, reason, (640, 520), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        
        # Add status information
        self.add_status_info(screen, today_scans)
        
        return screen
    
    def draw_qr_icon(self, screen, x, y, size=80):
        """Draw a simple QR code icon"""
        # Draw outer square
        cv2.rectangle(screen, (x-size, y-size), (x+size, y+size), (255, 255, 255), 3)
        
        # Draw inner squares (simplified QR pattern)
        small_size = size // 4
        cv2.rectangle(screen, (x-small_size, y-small_size), (x+small_size, y+small_size), (255, 255, 255), -1)
        cv2.rectangle(screen, (x-size+10, y-size+10), (x-size+30, y-size+30), (255, 255, 255), -1)
        cv2.rectangle(screen, (x+size-30, y-size+10), (x+size-10, y-size+30), (255, 255, 255), -1)
        cv2.rectangle(screen, (x-size+10, y+size-30), (x-size+30, y+size-10), (255, 255, 255), -1)
    
    def draw_tick_mark(self, screen, x, y, size=100, color=(0, 255, 0)):
        """Draw a green tick mark"""
        # Draw tick mark using lines
        thickness = 8
        # Vertical line
        cv2.line(screen, (x-20, y-20), (x-5, y-5), color, thickness)
        # Horizontal line
        cv2.line(screen, (x-5, y-5), (x+30, y-40), color, thickness)
    
    def draw_x_mark(self, screen, x, y, size=100, color=(0, 0, 255)):
        """Draw a red X mark"""
        thickness = 8
        # Diagonal lines
        cv2.line(screen, (x-size//2, y-size//2), (x+size//2, y+size//2), color, thickness)
        cv2.line(screen, (x+size//2, y-size//2), (x-size//2, y+size//2), color, thickness)
    
    def add_status_info(self, screen, today_scans):
        """Add status information to screen"""
        # Current date and time
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        cv2.putText(screen, f"Date: {date_str}", (50, 650), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(screen, f"Time: {time_str}", (50, 680), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Today's scan count
        cv2.putText(screen, f"Today's Scans: {today_scans}", (50, 710), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Online/Offline status
        status_color = (0, 255, 0) if self.is_online else (0, 0, 255)
        status_text = "ONLINE" if self.is_online else "OFFLINE"
        
        cv2.putText(screen, f"Status: {status_text}", (1000, 650), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        
        # Connection indicator dot
        dot_color = (0, 255, 0) if self.is_online else (0, 0, 255)
        cv2.circle(screen, (970, 650), 8, dot_color, -1)
    
    def update_connection_status(self):
        """Update internet connection status"""
        self.is_online = self.check_internet_connection()
    
    def can_scan(self):
        """Check if enough time has passed since last scan"""
        current_time = time.time()
        return current_time - self.last_scan_time > self.scan_cooldown
    
    def mark_scan_time(self):
        """Mark the current time as last scan time"""
        self.last_scan_time = time.time()
    
    def show_screen(self, screen):
        """Display the screen"""
        cv2.imshow(self.window_name, screen)
    
    def setup_fullscreen(self):
        """Setup fullscreen window"""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    def cleanup(self):
        """Cleanup display resources"""
        cv2.destroyAllWindows()

def test_display_manager():
    """Test display manager functionality"""
    print("🧪 Testing Display Manager...")
    
    dm = DisplayManager("AttractionA")
    dm.setup_fullscreen()
    
    # Test waiting screen
    waiting_screen = dm.create_waiting_screen(5)
    dm.show_screen(waiting_screen)
    cv2.waitKey(2000)
    
    # Test success screen
    ticket_info = {'persons_allowed': 2, 'persons_entered': 1}
    success_screen = dm.create_success_screen(ticket_info, 6)
    dm.show_screen(success_screen)
    cv2.waitKey(2000)
    
    # Test error screen
    error_screen = dm.create_error_screen("QR already scanned", 6)
    dm.show_screen(error_screen)
    cv2.waitKey(2000)
    
    dm.cleanup()
    print("✅ Display manager test completed!")

if __name__ == "__main__":
    test_display_manager()
