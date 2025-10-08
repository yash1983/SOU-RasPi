#!/usr/bin/env python3
"""
Simple USB Camera Test Script for Raspberry Pi
This script tests if the USB camera is accessible and working.
"""

import cv2
import sys
import time

def test_camera():
    """Test if USB camera is accessible"""
    print("🔍 Testing USB Camera Connection...")
    
    # Try to open camera (usually index 0 for USB cameras)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        print("Trying alternative camera indices...")
        
        # Try different camera indices
        for i in range(1, 5):
            print(f"Trying camera index {i}...")
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"✅ Camera found at index {i}")
                break
        else:
            print("❌ No camera found on any index")
            return False
    
    # Set lower resolution for 1GB RAM optimization
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 15)
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"✅ Camera connected successfully!")
    print(f"   Resolution: {width}x{height} (optimized for 1GB RAM)")
    print(f"   FPS: {fps}")
    
    # Test capturing a frame
    print("📸 Testing frame capture...")
    ret, frame = cap.read()
    
    if ret:
        print("✅ Frame captured successfully!")
        print(f"   Frame shape: {frame.shape}")
    else:
        print("❌ Failed to capture frame")
        cap.release()
        return False
    
    # Test live preview for 5 seconds
    print("🎥 Starting 5-second live preview...")
    print("   Press 'q' to quit early, or wait for auto-close")
    
    start_time = time.time()
    while time.time() - start_time < 5:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame during preview")
            break
            
        # Display the frame
        cv2.imshow('Camera Test - Press q to quit', frame)
        
        # Break if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print("✅ Camera test completed successfully!")
    return True

def main():
    """Main function"""
    print("=" * 50)
    print("📷 SOU Raspberry Pi - USB Camera Test")
    print("=" * 50)
    
    try:
        success = test_camera()
        
        if success:
            print("\n🎉 Camera is working! Ready for QR code scanning.")
        else:
            print("\n❌ Camera test failed. Please check:")
            print("   - USB camera is connected")
            print("   - Camera is not being used by another application")
            print("   - Camera drivers are installed")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

