#!/usr/bin/env python3
"""
QR Code Scanner for SOU Raspberry Pi
This script uses the USB camera to scan QR codes in real-time.
"""

import cv2
import sys
import time
from pyzbar import pyzbar

def scan_qr_codes():
    """Scan QR codes using USB camera"""
    print("📱 Starting QR Code Scanner...")
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return False
    
    print("✅ Camera opened successfully")
    print("📱 Point camera at QR code to scan")
    print("   Press 'q' to quit")
    print("   Press 's' to save current frame")
    
    last_scan_time = 0
    scan_cooldown = 1.0  # Minimum time between scans (seconds)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break
        
        # Resize frame for better performance
        frame = cv2.resize(frame, (640, 480))
        
        # Scan for QR codes
        current_time = time.time()
        if current_time - last_scan_time > scan_cooldown:
            qr_codes = pyzbar.decode(frame)
            
            if qr_codes:
                for qr_code in qr_codes:
                    # Extract QR code data
                    qr_data = qr_code.data.decode('utf-8')
                    qr_type = qr_code.type
                    
                    print(f"🔍 QR Code detected!")
                    print(f"   Type: {qr_type}")
                    print(f"   Data: {qr_data}")
                    print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print("-" * 40)
                    
                    # Draw rectangle around QR code
                    rect = qr_code.rect
                    cv2.rectangle(frame, (rect.left, rect.top), 
                                (rect.left + rect.width, rect.top + rect.height), 
                                (0, 255, 0), 2)
                    
                    # Add text overlay
                    cv2.putText(frame, f"QR: {qr_data[:20]}...", 
                              (rect.left, rect.top - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                last_scan_time = current_time
        
        # Add instructions overlay
        cv2.putText(frame, "Point camera at QR code", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Display frame
        cv2.imshow('SOU QR Code Scanner', frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("👋 Quitting QR scanner...")
            break
        elif key == ord('s'):
            # Save current frame
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"qr_scan_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"💾 Frame saved as {filename}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    return True

def main():
    """Main function"""
    print("=" * 50)
    print("📱 SOU Raspberry Pi - QR Code Scanner")
    print("=" * 50)
    
    try:
        success = scan_qr_codes()
        
        if success:
            print("✅ QR scanner completed successfully!")
        else:
            print("❌ QR scanner failed")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
