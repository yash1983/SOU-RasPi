#!/usr/bin/env python3
"""
Simple Camera Test for SOU Raspberry Pi
Tests if the USB camera is working properly
"""

import cv2
import sys
import time

def test_camera():
    """Test camera functionality"""
    print("📷 SOU Raspberry Pi - Camera Test")
    print("=" * 40)
    
    # Try to open camera
    print("🔍 Attempting to open camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        print("Troubleshooting:")
        print("  - Check if USB camera is connected")
        print("  - Try: lsusb | grep -i camera")
        print("  - Check permissions: ls -la /dev/video*")
        print("  - Add user to video group: sudo usermod -a -G video $USER")
        return False
    
    print("✅ Camera opened successfully!")
    
    # Get camera properties
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"📐 Camera resolution: {int(width)}x{int(height)}")
    print(f"🎬 Camera FPS: {fps}")
    
    # Test frame capture
    print("📸 Testing frame capture...")
    ret, frame = cap.read()
    
    if not ret:
        print("❌ Error: Could not capture frame")
        cap.release()
        return False
    
    print("✅ Frame capture successful!")
    print(f"📊 Frame shape: {frame.shape}")
    
    # Test for 5 seconds
    print("🎥 Testing camera for 5 seconds...")
    print("   Press 'q' to quit early")
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 5:
        ret, frame = cap.read()
        if ret:
            frame_count += 1
            
            # Add text overlay
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Camera Test - Press 'q' to quit", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display frame
            cv2.imshow('SOU Camera Test', frame)
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("👋 Quit by user")
                break
        else:
            print("❌ Error: Failed to read frame")
            break
    
    # Calculate actual FPS
    elapsed_time = time.time() - start_time
    actual_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
    
    print(f"📊 Test results:")
    print(f"   Frames captured: {frame_count}")
    print(f"   Time elapsed: {elapsed_time:.2f} seconds")
    print(f"   Actual FPS: {actual_fps:.2f}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    if frame_count > 0:
        print("✅ Camera test completed successfully!")
        return True
    else:
        print("❌ Camera test failed!")
        return False

def main():
    """Main function"""
    try:
        success = test_camera()
        
        if success:
            print("\n🎉 Camera is working properly!")
            print("You can now run the attraction scanners:")
            print("  python3 AttractionA.py")
            print("  python3 AttractionB.py") 
            print("  python3 AttractionC.py")
            return 0
        else:
            print("\n❌ Camera test failed!")
            print("Please check camera connection and permissions.")
            return 1
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
