#!/usr/bin/env python3
"""
Database Reset Utility for SOU Raspberry Pi
Resets all attraction databases to initial state
"""

import sqlite3
import os
from datetime import datetime

class DatabaseReset:
    def __init__(self):
        """Initialize database reset utility"""
        self.attractions = ["AttractionA", "AttractionB", "AttractionC"]
    
    def reset_attraction_database(self, attraction_name):
        """Reset a single attraction database"""
        db_path = f"{attraction_name}.db"
        
        if not os.path.exists(db_path):
            print(f"⚠️  Database {db_path} not found, skipping...")
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Reset tickets table
            cursor.execute('''
                UPDATE tickets 
                SET persons_entered = 0,
                    is_synced = 0,
                    last_scan = NULL
            ''')
            
            tickets_reset = cursor.rowcount
            
            # Truncate scan_history table
            cursor.execute('DELETE FROM scan_history')
            history_deleted = cursor.rowcount
            
            # Reset auto-increment counter for scan_history
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="scan_history"')
            
            conn.commit()
            conn.close()
            
            print(f"✅ {attraction_name}: Reset {tickets_reset} tickets, deleted {history_deleted} scan records")
            return True
            
        except Exception as e:
            print(f"❌ Error resetting {attraction_name}: {e}")
            return False
    
    def reset_all_databases(self):
        """Reset all attraction databases"""
        print("🔄 SOU Raspberry Pi - Database Reset Utility")
        print("=" * 50)
        print(f"📅 Reset time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        success_count = 0
        total_count = len(self.attractions)
        
        for attraction in self.attractions:
            print(f"🔄 Resetting {attraction}...")
            if self.reset_attraction_database(attraction):
                success_count += 1
        
        print()
        print("=" * 50)
        print(f"📊 Reset Summary:")
        print(f"   Successful: {success_count}/{total_count} databases")
        print(f"   Failed: {total_count - success_count}/{total_count} databases")
        
        if success_count == total_count:
            print("✅ All databases reset successfully!")
            return True
        else:
            print("❌ Some databases failed to reset!")
            return False
    
    def show_database_status(self):
        """Show current status of all databases"""
        print("📊 Current Database Status")
        print("=" * 50)
        
        for attraction in self.attractions:
            db_path = f"{attraction}.db"
            
            if not os.path.exists(db_path):
                print(f"❌ {attraction}: Database not found")
                continue
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get ticket statistics
                cursor.execute('SELECT COUNT(*) FROM tickets')
                total_tickets = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM tickets WHERE persons_entered > 0')
                used_tickets = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM scan_history')
                total_scans = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM scan_history WHERE DATE(scan_time) = DATE("now")')
                today_scans = cursor.fetchone()[0]
                
                conn.close()
                
                print(f"📋 {attraction}:")
                print(f"   Total tickets: {total_tickets}")
                print(f"   Used tickets: {used_tickets}")
                print(f"   Total scans: {total_scans}")
                print(f"   Today's scans: {today_scans}")
                print()
                
            except Exception as e:
                print(f"❌ {attraction}: Error reading database - {e}")
    
    def backup_databases(self):
        """Create backup of all databases before reset"""
        print("💾 Creating database backups...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f"backup_{timestamp}"
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            for attraction in self.attractions:
                db_path = f"{attraction}.db"
                if os.path.exists(db_path):
                    backup_path = os.path.join(backup_dir, f"{attraction}.db")
                    import shutil
                    shutil.copy2(db_path, backup_path)
                    print(f"✅ Backed up {attraction}.db to {backup_path}")
            
            print(f"📁 All backups saved to: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None

def main():
    """Main function with interactive menu"""
    reset_util = DatabaseReset()
    
    while True:
        print("\n" + "=" * 50)
        print("🗄️  SOU Database Reset Utility")
        print("=" * 50)
        print("1. Show database status")
        print("2. Reset all databases")
        print("3. Reset specific attraction")
        print("4. Backup databases")
        print("5. Reset with backup")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            reset_util.show_database_status()
            
        elif choice == "2":
            confirm = input("⚠️  This will reset ALL databases. Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                reset_util.reset_all_databases()
            else:
                print("❌ Reset cancelled")
                
        elif choice == "3":
            print("\nSelect attraction to reset:")
            for i, attraction in enumerate(reset_util.attractions, 1):
                print(f"{i}. {attraction}")
            
            try:
                sub_choice = int(input("Enter number (1-3): ")) - 1
                if 0 <= sub_choice < len(reset_util.attractions):
                    attraction = reset_util.attractions[sub_choice]
                    confirm = input(f"⚠️  Reset {attraction}? (y/N): ").strip().lower()
                    if confirm == 'y':
                        reset_util.reset_attraction_database(attraction)
                    else:
                        print("❌ Reset cancelled")
                else:
                    print("❌ Invalid choice")
            except ValueError:
                print("❌ Invalid input")
                
        elif choice == "4":
            reset_util.backup_databases()
            
        elif choice == "5":
            print("🔄 Reset with backup...")
            backup_dir = reset_util.backup_databases()
            if backup_dir:
                confirm = input("⚠️  Proceed with reset after backup? (y/N): ").strip().lower()
                if confirm == 'y':
                    reset_util.reset_all_databases()
                else:
                    print("❌ Reset cancelled")
            
        elif choice == "6":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()
