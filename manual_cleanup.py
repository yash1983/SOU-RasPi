#!/usr/bin/env python3
"""
Manual Cleanup Utility for SOU Raspberry Pi
Allows manual execution of database cleanup for testing or emergency use
"""

import sys
from cleanup_service import CleanupService

def main():
    """Main function for manual cleanup"""
    print("[CLEANUP] SOU Manual Database Cleanup")
    print("=" * 40)
    
    # Create cleanup service instance
    service = CleanupService()
    
    # Show current database stats
    print("\n[STATS] Current Database Statistics:")
    stats = service.get_cleanup_stats()
    for attraction, data in stats.items():
        if 'error' in data:
            print(f"  {attraction}: {data['error']}")
        else:
            print(f"  {attraction}: {data['tickets']} tickets, {data['scans']} scans, {data['file_size_mb']} MB")
    
    # Ask for confirmation
    print(f"\n[WARNING] This will clean up data from yesterday and earlier.")
    print(f"   Current date: {service.get_yesterday_date()}")
    
    confirm = input("\nProceed with cleanup? (y/N): ").strip().lower()
    
    if confirm == 'y':
        print("\n[CLEANUP] Starting manual cleanup...")
        success = service.run_cleanup_cycle()
        
        if success:
            print("\n[SUCCESS] Manual cleanup completed successfully!")
        else:
            print("\n[ERROR] Manual cleanup completed with errors. Check logs for details.")
            sys.exit(1)
    else:
        print("\n[CANCELLED] Cleanup cancelled.")
        sys.exit(0)

if __name__ == "__main__":
    main()
