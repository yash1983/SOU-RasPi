#!/usr/bin/env python3
"""
Database Migration Script for SOU Raspberry Pi
Migrates existing database structure to new format
"""

import sqlite3
import os
import shutil
from datetime import datetime

class DatabaseMigrator:
    """Handles migration from old to new database structure"""
    
    def __init__(self):
        """Initialize migrator"""
        self.attractions = ["AttractionA", "AttractionB", "AttractionC"]
        self.backup_suffix = f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def backup_database(self, db_path):
        """Create backup of existing database"""
        if not os.path.exists(db_path):
            print(f"⚠️  Database {db_path} not found, skipping backup")
            return None
        
        backup_path = db_path + self.backup_suffix
        shutil.copy2(db_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        return backup_path
    
    def check_old_structure(self, db_path):
        """Check if database has old structure"""
        if not os.path.exists(db_path):
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if old columns exist
            cursor.execute("PRAGMA table_info(tickets)")
            columns = [row[1] for row in cursor.fetchall()]
            
            has_old_structure = (
                'persons_allowed' in columns and 
                'persons_entered' in columns and 
                'attractions' in columns
            )
            
            has_new_structure = (
                'A_pax' in columns and 
                'A_used' in columns and 
                'booking_date' in columns
            )
            
            conn.close()
            
            if has_old_structure and not has_new_structure:
                return True
            elif has_new_structure:
                print(f"✅ Database {db_path} already has new structure")
                return False
            else:
                print(f"⚠️  Database {db_path} has unknown structure")
                return False
                
        except Exception as e:
            print(f"❌ Error checking database structure: {e}")
            conn.close()
            return False
    
    def migrate_attraction_database(self, attraction_name):
        """Migrate a single attraction database"""
        db_path = f"{attraction_name}.db"
        
        print(f"\n🔄 Migrating {attraction_name} database...")
        
        # Check if migration is needed
        if not self.check_old_structure(db_path):
            return True
        
        # Create backup
        backup_path = self.backup_database(db_path)
        if not backup_path:
            return False
        
        try:
            # Create new database with new structure
            new_db_path = f"{attraction_name}_new.db"
            conn_new = sqlite3.connect(new_db_path)
            cursor_new = conn_new.cursor()
            
            # Create new table structure
            cursor_new.execute('''
                CREATE TABLE tickets (
                    ticket_no TEXT PRIMARY KEY,
                    booking_date TEXT NOT NULL,
                    reference_no TEXT NOT NULL,
                    A_pax INTEGER DEFAULT 0,
                    A_used INTEGER DEFAULT 0,
                    B_pax INTEGER DEFAULT 0,
                    B_used INTEGER DEFAULT 0,
                    C_pax INTEGER DEFAULT 0,
                    C_used INTEGER DEFAULT 0,
                    is_synced BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_scan TIMESTAMP
                )
            ''')
            
            cursor_new.execute('''
                CREATE TABLE scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_no TEXT NOT NULL,
                    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    result TEXT NOT NULL,
                    reason TEXT,
                    FOREIGN KEY (ticket_no) REFERENCES tickets (ticket_no)
                )
            ''')
            
            # Create indexes
            cursor_new.execute('CREATE INDEX idx_ticket_no ON tickets(ticket_no)')
            cursor_new.execute('CREATE INDEX idx_scan_time ON scan_history(scan_time)')
            cursor_new.execute('CREATE INDEX idx_is_synced ON tickets(is_synced)')
            cursor_new.execute('CREATE INDEX idx_last_scan ON tickets(last_scan)')
            cursor_new.execute('CREATE INDEX idx_scan_history_ticket ON scan_history(ticket_no)')
            
            # Read old data
            conn_old = sqlite3.connect(db_path)
            cursor_old = conn_old.cursor()
            
            cursor_old.execute('SELECT * FROM tickets')
            old_tickets = cursor_old.fetchall()
            
            cursor_old.execute('SELECT * FROM scan_history')
            old_history = cursor_old.fetchall()
            
            # Migrate tickets data
            migrated_count = 0
            for old_ticket in old_tickets:
                try:
                    # Extract old data (assuming old structure)
                    ticket_no = old_ticket[0]
                    persons_allowed = old_ticket[1]
                    persons_entered = old_ticket[2]
                    is_synced = old_ticket[3]
                    attractions = old_ticket[4]
                    created_at = old_ticket[5] if len(old_ticket) > 5 else None
                    last_scan = old_ticket[6] if len(old_ticket) > 6 else None
                    
                    # Parse attractions string (e.g., "A,B" or "A,B,C")
                    attraction_list = [a.strip() for a in attractions.split(',')]
                    
                    # Set default booking date and reference number
                    booking_date = "2025-01-01"  # Default date
                    reference_no = ticket_no
                    
                    # Initialize attraction data
                    a_pax = persons_allowed if 'A' in attraction_list else 0
                    a_used = persons_entered if 'A' in attraction_list else 0
                    b_pax = persons_allowed if 'B' in attraction_list else 0
                    b_used = persons_entered if 'B' in attraction_list else 0
                    c_pax = persons_allowed if 'C' in attraction_list else 0
                    c_used = persons_entered if 'C' in attraction_list else 0
                    
                    # Insert into new structure
                    cursor_new.execute('''
                        INSERT INTO tickets 
                        (ticket_no, booking_date, reference_no, A_pax, A_used, B_pax, B_used, C_pax, C_used, is_synced, created_at, last_scan)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (ticket_no, booking_date, reference_no, a_pax, a_used, b_pax, b_used, c_pax, c_used, is_synced, created_at, last_scan))
                    
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"⚠️  Error migrating ticket {old_ticket[0]}: {e}")
            
            # Migrate scan history
            for old_history_item in old_history:
                try:
                    cursor_new.execute('''
                        INSERT INTO scan_history (ticket_no, scan_time, result, reason)
                        VALUES (?, ?, ?, ?)
                    ''', (old_history_item[1], old_history_item[2], old_history_item[3], old_history_item[4]))
                except Exception as e:
                    print(f"⚠️  Error migrating history item: {e}")
            
            conn_new.commit()
            conn_new.close()
            conn_old.close()
            
            # Replace old database with new one
            os.remove(db_path)
            os.rename(new_db_path, db_path)
            
            print(f"✅ Successfully migrated {migrated_count} tickets for {attraction_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error migrating {attraction_name}: {e}")
            # Restore backup if migration failed
            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, db_path)
                print(f"🔄 Restored backup for {attraction_name}")
            return False
    
    def migrate_all_databases(self):
        """Migrate all attraction databases"""
        print("🚀 Starting database migration...")
        print("=" * 50)
        
        success_count = 0
        
        for attraction in self.attractions:
            if self.migrate_attraction_database(attraction):
                success_count += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Migration completed: {success_count}/{len(self.attractions)} databases migrated successfully")
        
        if success_count == len(self.attractions):
            print("✅ All databases migrated successfully!")
            return True
        else:
            print("⚠️  Some databases failed to migrate. Check the logs above.")
            return False

def main():
    """Main entry point for migration"""
    migrator = DatabaseMigrator()
    
    print("⚠️  WARNING: This will modify your existing databases!")
    print("Backups will be created automatically.")
    
    response = input("Do you want to continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    success = migrator.migrate_all_databases()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now use the new database structure.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")

if __name__ == "__main__":
    main()
