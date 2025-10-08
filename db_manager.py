#!/usr/bin/env python3
"""
Database Manager for SOU Raspberry Pi
Interactive tool to manage SQLite database with 1000 record limit
"""

import sys
from database_manager import QRDatabase

def show_menu():
    """Display main menu"""
    print("\n" + "="*50)
    print("🗄️  SOU Raspberry Pi - Database Manager")
    print("="*50)
    print("1. Show database statistics")
    print("2. View recent scans")
    print("3. Search scans")
    print("4. Set record limit")
    print("5. Cleanup old scans")
    print("6. Test database")
    print("7. Exit")

def main():
    """Main function"""
    db = QRDatabase()
    
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            print("\n" + "="*30)
            stats = db.get_stats()
            print(f"📊 Database Statistics:")
            print(f"   Total scans: {stats['total_scans']}")
            print(f"   Today's scans: {stats['today_scans']}")
            print(f"   Unique codes: {stats['unique_codes']}")
            print(f"   Database size: {stats['db_size_mb']} MB")
            print(f"   Records used: {stats['records_used']}/{stats['max_records']}")
            
        elif choice == "2":
            print("\n" + "="*30)
            limit = input("How many recent scans to show? (default 10): ").strip()
            try:
                limit = int(limit) if limit else 10
                recent = db.get_recent_scans(limit)
                print(f"📋 Recent {len(recent)} scans:")
                for scan in recent:
                    print(f"   ID: {scan[0]} | {scan[2]} | {scan[1][:30]}... | {scan[3]}")
            except ValueError:
                print("❌ Invalid number")
                
        elif choice == "3":
            print("\n" + "="*30)
            search_term = input("Enter search term: ").strip()
            if search_term:
                results = db.search_scans(search_term)
                print(f"🔍 Found {len(results)} matching scans:")
                for result in results:
                    print(f"   ID: {result[0]} | {result[2]} | {result[1]} | {result[3]}")
            else:
                print("❌ Please enter a search term")
                
        elif choice == "4":
            print("\n" + "="*30)
            try:
                new_limit = int(input("Enter new record limit (default 1000): ") or "1000")
                deleted = db.set_record_limit(new_limit)
                print(f"✅ Record limit set to {new_limit}")
            except ValueError:
                print("❌ Invalid number entered")
                
        elif choice == "5":
            print("\n" + "="*30)
            try:
                days = int(input("Remove scans older than how many days? (default 30): ") or "30")
                deleted = db.cleanup_old_scans(days)
                print(f"✅ Cleanup completed")
            except ValueError:
                print("❌ Invalid number entered")
                
        elif choice == "6":
            print("\n" + "="*30)
            print("🧪 Testing database functionality...")
            try:
                # Add test scan
                test_id = db.add_scan("TEST_SCAN_123", "QRCODE", 0, "test.jpg")
                print(f"✅ Test scan added with ID: {test_id}")
                
                # Get stats
                stats = db.get_stats()
                print(f"✅ Database stats retrieved: {stats['total_scans']} total scans")
                
                print("✅ Database test completed successfully!")
            except Exception as e:
                print(f"❌ Database test failed: {e}")
                
        elif choice == "7":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-7.")

if __name__ == "__main__":
    main()
