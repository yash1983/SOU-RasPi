#!/usr/bin/env python3
"""
Ticket Database Manager for SOU Raspberry Pi
Manages ticket validation for multiple attractions
"""

import sqlite3
import os
from datetime import datetime

class TicketDatabase:
    def __init__(self, attraction_name):
        """Initialize database for specific attraction"""
        self.attraction_name = attraction_name
        self.db_path = f"{attraction_name}.db"
        self.init_database()
    
    def init_database(self):
        """Create database and tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Optimize SQLite for better performance on Raspberry Pi
        cursor.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging for better concurrency
        cursor.execute('PRAGMA synchronous=NORMAL')  # Balance between safety and speed
        cursor.execute('PRAGMA cache_size=10000')  # Increase cache size for 4GB RAM
        cursor.execute('PRAGMA temp_store=MEMORY')  # Store temp tables in memory
        cursor.execute('PRAGMA mmap_size=268435456')  # 256MB memory mapping
        
        # Create tickets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_no TEXT PRIMARY KEY,
                persons_allowed INTEGER NOT NULL,
                persons_entered INTEGER DEFAULT 0,
                is_synced BOOLEAN DEFAULT 0,
                attractions TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_scan TIMESTAMP
            )
        ''')
        
        # Create scan history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_no TEXT NOT NULL,
                scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                result TEXT NOT NULL,
                reason TEXT,
                FOREIGN KEY (ticket_no) REFERENCES tickets (ticket_no)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticket_no ON tickets(ticket_no)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scan_time ON scan_history(scan_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_synced ON tickets(is_synced)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_scan ON tickets(last_scan)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scan_history_ticket ON scan_history(ticket_no)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_attractions ON tickets(attractions)')
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized for {self.attraction_name}: {self.db_path}")
    
    def add_ticket(self, ticket_no, persons_allowed, attractions):
        """Add a new ticket to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO tickets (ticket_no, persons_allowed, persons_entered, is_synced, attractions)
                VALUES (?, ?, 0, 0, ?)
            ''', (ticket_no, persons_allowed, attractions))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error adding ticket: {e}")
            conn.close()
            return False
    
    def add_tickets_bulk(self, tickets_data):
        """Add multiple tickets to the database in a single transaction for better performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Apply performance optimizations for bulk operations
        cursor.execute('PRAGMA synchronous=OFF')  # Disable sync for bulk inserts
        cursor.execute('PRAGMA journal_mode=MEMORY')  # Use memory journal for bulk operations
        
        try:
            cursor.executemany('''
                INSERT OR REPLACE INTO tickets (ticket_no, persons_allowed, persons_entered, is_synced, attractions)
                VALUES (?, ?, 0, 0, ?)
            ''', tickets_data)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error adding tickets in bulk: {e}")
            conn.close()
            return False
    
    def validate_ticket(self, ticket_no):
        """Validate ticket and return validation result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Optimize for performance - use single query with conditional update
        cursor.execute('''
            SELECT persons_allowed, persons_entered, is_synced
            FROM tickets
            WHERE ticket_no = ?
        ''', (ticket_no,))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return {
                'valid': False,
                'reason': 'Invalid QR - Ticket not found',
                'persons_allowed': 0,
                'persons_entered': 0
            }
        
        persons_allowed, persons_entered, is_synced = result
        
        # Check if all persons have already entered
        if persons_entered >= persons_allowed:
            conn.close()
            return {
                'valid': False,
                'reason': 'QR already scanned - All entries used',
                'persons_allowed': persons_allowed,
                'persons_entered': persons_entered
            }
        
        # Ticket is valid, increment persons_entered with optimized query
        cursor.execute('''
            UPDATE tickets
            SET persons_entered = persons_entered + 1,
                last_scan = CURRENT_TIMESTAMP
            WHERE ticket_no = ? AND persons_entered < persons_allowed
        ''', (ticket_no,))
        
        # Check if update was successful (prevents race conditions)
        if cursor.rowcount == 0:
            conn.close()
            return {
                'valid': False,
                'reason': 'QR already scanned - All entries used',
                'persons_allowed': persons_allowed,
                'persons_entered': persons_entered
            }
        
        conn.commit()
        conn.close()
        
        return {
            'valid': True,
            'reason': 'Valid Entry',
            'persons_allowed': persons_allowed,
            'persons_entered': persons_entered + 1
        }
    
    def validate_and_log_ticket(self, ticket_no, attraction_name):
        """Validate ticket and log result in a single optimized transaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Optimize for performance
        cursor.execute('PRAGMA synchronous=NORMAL')
        
        # Check if ticket exists and is valid for this attraction
        cursor.execute('''
            SELECT persons_allowed, persons_entered, is_synced, attractions
            FROM tickets
            WHERE ticket_no = ?
        ''', (ticket_no,))
        
        result = cursor.fetchone()
        
        if not result:
            # Log failed scan
            cursor.execute('''
                INSERT INTO scan_history (ticket_no, result, reason)
                VALUES (?, 'FAILED', 'Invalid QR - Ticket not found')
            ''', (ticket_no,))
            conn.commit()
            conn.close()
            return {
                'valid': False,
                'reason': 'Invalid QR - Ticket not found',
                'persons_allowed': 0,
                'persons_entered': 0
            }
        
        persons_allowed, persons_entered, is_synced, attractions = result
        
        # Check if ticket is valid for this attraction
        if attraction_name not in attractions:
            # Log failed scan
            reason = f'Attraction mismatch - Ticket not valid for {attraction_name}'
            cursor.execute('''
                INSERT INTO scan_history (ticket_no, result, reason)
                VALUES (?, 'FAILED', ?)
            ''', (ticket_no, reason))
            conn.commit()
            conn.close()
            return {
                'valid': False,
                'reason': reason,
                'persons_allowed': persons_allowed,
                'persons_entered': persons_entered
            }
        
        # Check if all persons have already entered
        if persons_entered >= persons_allowed:
            # Log failed scan
            cursor.execute('''
                INSERT INTO scan_history (ticket_no, result, reason)
                VALUES (?, 'FAILED', 'QR already scanned - All entries used')
            ''', (ticket_no,))
            conn.commit()
            conn.close()
            return {
                'valid': False,
                'reason': 'QR already scanned - All entries used',
                'persons_allowed': persons_allowed,
                'persons_entered': persons_entered
            }
        
        # Ticket is valid, increment persons_entered and log success
        cursor.execute('''
            UPDATE tickets
            SET persons_entered = persons_entered + 1,
                last_scan = CURRENT_TIMESTAMP
            WHERE ticket_no = ? AND persons_entered < persons_allowed
        ''', (ticket_no,))
        
        # Check if update was successful
        if cursor.rowcount == 0:
            # Log failed scan
            cursor.execute('''
                INSERT INTO scan_history (ticket_no, result, reason)
                VALUES (?, 'FAILED', 'QR already scanned - All entries used')
            ''', (ticket_no,))
            conn.commit()
            conn.close()
            return {
                'valid': False,
                'reason': 'QR already scanned - All entries used',
                'persons_allowed': persons_allowed,
                'persons_entered': persons_entered
            }
        
        # Log successful scan
        cursor.execute('''
            INSERT INTO scan_history (ticket_no, result, reason)
            VALUES (?, 'SUCCESS', 'Valid Entry')
        ''', (ticket_no,))
        
        conn.commit()
        conn.close()
        
        return {
            'valid': True,
            'reason': 'Valid Entry',
            'persons_allowed': persons_allowed,
            'persons_entered': persons_entered + 1
        }
    
    def log_scan(self, ticket_no, result, reason):
        """Log scan attempt to history - optimized for performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Use optimized settings for logging
        cursor.execute('PRAGMA synchronous=OFF')  # Faster writes for logging
        
        cursor.execute('''
            INSERT INTO scan_history (ticket_no, result, reason)
            VALUES (?, ?, ?)
        ''', (ticket_no, result, reason))
        
        conn.commit()
        conn.close()
    
    def get_today_scans(self):
        """Get count of scans today"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM scan_history
            WHERE DATE(scan_time) = DATE('now')
        ''')
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_ticket_info(self, ticket_no):
        """Get detailed ticket information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT persons_allowed, persons_entered, is_synced, created_at, last_scan
            FROM tickets
            WHERE ticket_no = ?
        ''', (ticket_no,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'persons_allowed': result[0],
                'persons_entered': result[1],
                'is_synced': result[2],
                'created_at': result[3],
                'last_scan': result[4]
            }
        return None
    
    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total tickets
        cursor.execute('SELECT COUNT(*) FROM tickets')
        total_tickets = cursor.fetchone()[0]
        
        # Today's scans
        today_scans = self.get_today_scans()
        
        # Total entries today
        cursor.execute('''
            SELECT SUM(persons_entered) FROM tickets
            WHERE DATE(last_scan) = DATE('now')
        ''')
        today_entries = cursor.fetchone()[0] or 0
        
        # Unsynced records count
        cursor.execute('SELECT COUNT(*) FROM tickets WHERE is_synced = 0')
        unsynced_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_tickets': total_tickets,
            'today_scans': today_scans,
            'today_entries': today_entries,
            'unsynced_count': unsynced_count,
            'attraction_name': self.attraction_name
        }
    
    def add_sample_tickets(self):
        """Add sample tickets for testing"""
        sample_tickets = [
            ("TICKET_A_001_2P", 2, "A"),  # 2 persons for Attraction A
            ("TICKET_A_002_1P", 1, "A"),  # 1 person for Attraction A
            ("TICKET_AB_001_3P", 3, "A,B"), # 3 persons for Attraction A & B
            ("TICKET_ABC_001_4P", 4, "A,B,C"), # 4 persons for all attractions
        ]
        
        for ticket_no, persons, attractions in sample_tickets:
            self.add_ticket(ticket_no, persons, attractions)
        
        print(f"✅ Added {len(sample_tickets)} sample tickets to {self.attraction_name}")

def test_ticket_database():
    """Test ticket database functionality"""
    print("🧪 Testing Ticket Database...")
    
    # Test Attraction A
    db_a = TicketDatabase("AttractionA")
    db_a.add_sample_tickets()
    
    # Test validation
    result = db_a.validate_ticket("TICKET_A_001_2P")
    print(f"Validation result: {result}")
    
    # Test stats
    stats = db_a.get_stats()
    print(f"Stats: {stats}")
    
    print("✅ Ticket database test completed!")

if __name__ == "__main__":
    test_ticket_database()
