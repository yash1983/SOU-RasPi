#!/usr/bin/env python3
"""
SOU Raspberry Pi - Test Runner
This script helps you run different tests step by step.
"""

import sys
import subprocess
import os

def run_camera_test():
    """Run camera test"""
    print("🔍 Running camera test...")
    try:
        result = subprocess.run([sys.executable, "camera_test.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running camera test: {e}")
        return False

def run_qr_scanner():
    """Run QR scanner"""
    print("📱 Starting QR scanner...")
    try:
        subprocess.run([sys.executable, "qr_scanner.py"])
        return True
    except Exception as e:
        print(f"❌ Error running QR scanner: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("🧪 SOU Raspberry Pi - Test Runner")
    print("=" * 50)
    
    while True:
        print("\nChoose a test to run:")
        print("1. Camera Test (test if camera works)")
        print("2. QR Scanner (scan QR codes)")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n" + "="*30)
            success = run_camera_test()
            if success:
                print("✅ Camera test passed!")
            else:
                print("❌ Camera test failed!")
                
        elif choice == "2":
            print("\n" + "="*30)
            run_qr_scanner()
            
        elif choice == "3":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
