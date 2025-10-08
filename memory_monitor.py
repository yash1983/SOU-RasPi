#!/usr/bin/env python3
"""
Memory Monitor for SOU Raspberry Pi (1GB RAM)
Monitors system memory usage and provides recommendations
"""

import psutil
import time
import os

def get_memory_info():
    """Get current memory usage"""
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        'total_gb': round(memory.total / (1024**3), 2),
        'available_gb': round(memory.available / (1024**3), 2),
        'used_gb': round(memory.used / (1024**3), 2),
        'percent_used': memory.percent,
        'swap_used_gb': round(swap.used / (1024**3), 2),
        'swap_percent': swap.percent
    }

def check_memory_status():
    """Check if memory usage is acceptable"""
    info = get_memory_info()
    
    print(f"💾 Memory Status:")
    print(f"   Total RAM: {info['total_gb']} GB")
    print(f"   Used RAM: {info['used_gb']} GB ({info['percent_used']}%)")
    print(f"   Available: {info['available_gb']} GB")
    print(f"   Swap Used: {info['swap_used_gb']} GB ({info['swap_percent']}%)")
    
    # Recommendations
    if info['percent_used'] > 90:
        print("⚠️  WARNING: Memory usage is very high!")
        print("   Recommendations:")
        print("   - Close unnecessary applications")
        print("   - Reduce camera resolution further")
        print("   - Consider adding swap space")
    elif info['percent_used'] > 75:
        print("⚠️  CAUTION: Memory usage is high")
        print("   Monitor closely during QR scanning")
    else:
        print("✅ Memory usage is acceptable")
    
    return info['percent_used'] < 90

def monitor_memory_continuous(duration=60):
    """Monitor memory for specified duration"""
    print(f"🔍 Monitoring memory for {duration} seconds...")
    print("Press Ctrl+C to stop early")
    
    start_time = time.time()
    max_usage = 0
    
    try:
        while time.time() - start_time < duration:
            info = get_memory_info()
            max_usage = max(max_usage, info['percent_used'])
            
            print(f"\r💾 RAM: {info['percent_used']}% | Available: {info['available_gb']} GB | Max: {max_usage}%", end='', flush=True)
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
    
    print(f"\n📊 Monitoring Summary:")
    print(f"   Maximum RAM usage: {max_usage}%")
    print(f"   Duration: {int(time.time() - start_time)} seconds")

def main():
    """Main function"""
    print("=" * 50)
    print("💾 SOU Raspberry Pi - Memory Monitor (1GB RAM)")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. Check current memory status")
        print("2. Monitor memory for 60 seconds")
        print("3. Monitor memory for 5 minutes")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\n" + "="*30)
            check_memory_status()
            
        elif choice == "2":
            print("\n" + "="*30)
            monitor_memory_continuous(60)
            
        elif choice == "3":
            print("\n" + "="*30)
            monitor_memory_continuous(300)
            
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
