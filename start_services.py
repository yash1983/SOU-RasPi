#!/usr/bin/env python3
"""
Start Services Script for SOU Raspberry Pi
Simple script to start background services
"""

import sys
import os
from service_manager import ServiceManager

def main():
    """Start all background services"""
    print("🚀 Starting SOU Background Services...")
    print("=" * 50)
    
    try:
        manager = ServiceManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n🛑 Services stopped by user")
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
