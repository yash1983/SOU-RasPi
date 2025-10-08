#!/usr/bin/env python3
"""
Optimized QR Code Scanner for SOU Raspberry Pi (1GB RAM)
Includes SQLite database integration for 2 lakh records
"""

import cv2
import sys
import time
from pyzbar import pyzbar
from database_manager import QRDatabase

def scan_qr_codes_optimized():
    """Optimized QR code scanner for 1GB RAM"""
    print("📱 Starting Optimized QR Code Scanner (1GB RAM)...")
    
    # Initialize database
    db = QRDatabase()
    
    # Initialize camera with low resolution
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return False
    
    # Set low resolution for 1GB RAM
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 10)  # Lower FPS to save CPU/RAM
    
    print("✅ Camera opened (320x240, 10 FPS - optimized for 1GB RAM)")
    print("📱 Point camera at QR code to scan")
    print("   Press 'q' to quit")
    print("   Press 's' to show stats")
    print("   Press 'c' to cleanup old scans")
    print("   Press 'l' to set record limit")
    
    last_scan_time = 0
    scan_cooldown = 2.0  # Longer cooldown to reduce CPU usage
    scan_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break
        
        # Scan for QR codes (less frequently to save CPU)
        current_time = time.time()
        if current_time - last_scan_time > scan_cooldown:
            qr_codes = pyzbar.decode(frame)
            
            if qr_codes:
                for qr_code in qr_codes:
                    # Extract QR code data
                    qr_data = qr_code.data.decode('utf-8')
                    qr_type = qr_code.type
                    
                    # Save to database
                    scan_id = db.add_scan(qr_data, qr_type, 0)
                    scan_count += 1
                    
                    print(f"🔍 QR Code #{scan_id} detected!")
                    print(f"   Type: {qr_type}")
                    print(f"   Data: {qr_data}")
                    print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Total scans: {scan_count}")
                    print("-" * 40)
                    
                    # Draw rectangle around QR code
                    rect = qr_code.rect
                    cv2.rectangle(frame, (rect.left, rect.top), 
                                (rect.left + rect.width, rect.top + rect.height), 
                                (0, 255, 0), 2)
                    
                    # Add text overlay
                    cv2.putText(frame, f"QR: {qr_data[:15]}...", 
                              (rect.left, rect.top - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                
                last_scan_time = current_time
        
        # Add status overlay
        cv2.putText(frame, f"Scans: {scan_count}", (10, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, "Press 'q' quit, 's' stats, 'c' cleanup", (10, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        # Display frame
        cv2.imshow('SOU QR Scanner (1GB RAM)', frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("👋 Quitting QR scanner...")
            break
        elif key == ord('s'):
            # Show database stats
            stats = db.get_stats()
            print(f"📊 Database Stats:")
            print(f"   Total scans: {stats['total_scans']}")
            print(f"   Today's scans: {stats['today_scans']}")
            print(f"   Unique codes: {stats['unique_codes']}")
            print(f"   DB size: {stats['db_size_mb']} MB")
            print(f"   Records: {stats['records_used']}/{stats['max_records']} (auto-cleanup at 1000)")
        elif key == ord('c'):
            # Cleanup old scans
            deleted = db.cleanup_old_scans(30)
            print(f"🗑️ Cleaned up {deleted} old scans")
        elif key == ord('l'):
            # Set record limit
            try:
                new_limit = int(input("Enter new record limit (default 1000): ") or "1000")
                deleted = db.set_record_limit(new_limit)
                print(f"✅ Record limit set to {new_limit}")
            except ValueError:
                print("❌ Invalid number entered")
    
    # Final stats
    final_stats = db.get_stats()
    print(f"\n📊 Final Stats:")
    print(f"   Total scans in session: {scan_count}")
    print(f"   Total scans in database: {final_stats['total_scans']}")
    print(f"   Database size: {final_stats['db_size_mb']} MB")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    return True

def main():
    """Main function"""
    print("=" * 50)
    print("📱 SOU Raspberry Pi - Optimized QR Scanner (1GB RAM)")
    print("=" * 50)
    
    try:
        success = scan_qr_codes_optimized()
        
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
