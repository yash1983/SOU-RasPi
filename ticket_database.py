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
        
        # Create tickets table with new structure
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_booking_date ON tickets(booking_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reference_no ON tickets(reference_no)')
        
        conn.commit()
        conn.close()
        print(f"Database initialized for {self.attraction_name}: {self.db_path}")
    
    def add_ticket(self, ticket_no, booking_date, reference_no, attractions_data):
        """Add a new ticket to the database with new structure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Extract attraction data
            a_pax = attractions_data.get('A', {}).get('pax', 0)
            a_used = attractions_data.get('A', {}).get('used', 0)
            b_pax = attractions_data.get('B', {}).get('pax', 0)
            b_used = attractions_data.get('B', {}).get('used', 0)
            c_pax = attractions_data.get('C', {}).get('pax', 0)
            c_used = attractions_data.get('C', {}).get('used', 0)
            
            cursor.execute('''
                INSERT OR REPLACE INTO tickets 
                (ticket_no, booking_date, reference_no, A_pax, A_used, B_pax, B_used, C_pax, C_used, is_synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (ticket_no, booking_date, reference_no, a_pax, a_used, b_pax, b_used, c_pax, c_used))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding ticket: {e}")
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
                INSERT OR REPLACE INTO tickets 
                (ticket_no, booking_date, reference_no, A_pax, A_used, B_pax, B_used, C_pax, C_used, is_synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', tickets_data)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding tickets in bulk: {e}")
            conn.close()
            return False
    
    def validate_ticket(self, ticket_no, attraction_name):
        """Validate ticket and return validation result for specific attraction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Normalize attraction name (handle both "A" and "AttractionA" formats)
        if attraction_name.startswith("Attraction"):
            attraction_short = attraction_name[-1]  # Get last character (A, B, or C)
        else:
            attraction_short = attraction_name.upper()
        
        # Get ticket data for the specific attraction
        attraction_col = f"{attraction_short}_pax"
        used_col = f"{attraction_short}_used"
        
        cursor.execute(f'''
            SELECT {attraction_col}, {used_col}, is_synced
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
        
        # Check if ticket is valid for this attraction
        if persons_allowed == 0:
            conn.close()
            return {
                'valid': False,
                'reason': f'Attraction mismatch - Ticket not valid for {attraction_short}',
                'persons_allowed': 0,
                'persons_entered': 0
            }
        
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
        cursor.execute(f'''
            UPDATE tickets
            SET {used_col} = {used_col} + 1,
                is_synced = 0,
                last_scan = CURRENT_TIMESTAMP
            WHERE ticket_no = ? AND {used_col} < {attraction_col}
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
        
        # Normalize attraction name (handle both "A" and "AttractionA" formats)
        if attraction_name.startswith("Attraction"):
            attraction_short = attraction_name[-1]  # Get last character (A, B, or C)
        else:
            attraction_short = attraction_name.upper()
        
        # Get ticket data for the specific attraction
        attraction_col = f"{attraction_short}_pax"
        used_col = f"{attraction_short}_used"
        
        cursor.execute(f'''
            SELECT {attraction_col}, {used_col}, is_synced
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
        
        persons_allowed, persons_entered, is_synced = result
        
        # Check if ticket is valid for this attraction
        if persons_allowed == 0:
            # Log failed scan
            reason = f'Attraction mismatch - Ticket not valid for {attraction_short}'
            cursor.execute('''
                INSERT INTO scan_history (ticket_no, result, reason)
                VALUES (?, 'FAILED', ?)
            ''', (ticket_no, reason))
            conn.commit()
            conn.close()
            return {
                'valid': False,
                'reason': reason,
                'persons_allowed': 0,
                'persons_entered': 0
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
        cursor.execute(f'''
            UPDATE tickets
            SET {used_col} = {used_col} + 1,
                is_synced = 0,
                last_scan = CURRENT_TIMESTAMP
            WHERE ticket_no = ? AND {used_col} < {attraction_col}
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
            SELECT booking_date, reference_no, A_pax, A_used, B_pax, B_used, C_pax, C_used, 
                   is_synced, created_at, last_scan
            FROM tickets
            WHERE ticket_no = ?
        ''', (ticket_no,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'booking_date': result[0],
                'reference_no': result[1],
                'A_pax': result[2],
                'A_used': result[3],
                'B_pax': result[4],
                'B_used': result[5],
                'C_pax': result[6],
                'C_used': result[7],
                'is_synced': result[8],
                'created_at': result[9],
                'last_scan': result[10]
            }
        return None
    
    def get_ticket_for_sync(self, ticket_no):
        """Get ticket data in format for server sync"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT booking_date, reference_no, A_pax, A_used, B_pax, B_used, C_pax, C_used
            FROM tickets
            WHERE ticket_no = ?
        ''', (ticket_no,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            booking_date, reference_no, a_pax, a_used, b_pax, b_used, c_pax, c_used = result
            return {
                "BookingDate": booking_date,
                "ReferenceNo": reference_no,
                "Attractions": {
                    "A": {"pax": a_pax, "used": a_used},
                    "B": {"pax": b_pax, "used": b_used},
                    "C": {"pax": c_pax, "used": c_used}
                }
            }
        return None
    
    def get_unsynced_tickets(self):
        """Get all unsynced tickets for background sync service"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ticket_no FROM tickets WHERE is_synced = 0
            ORDER BY last_scan ASC, created_at ASC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in results]
    
    def mark_ticket_synced(self, ticket_no):
        """Mark a ticket as synced"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tickets SET is_synced = 1 WHERE ticket_no = ?
        ''', (ticket_no,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def ticket_exists(self, ticket_no):
        """Check if ticket exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM tickets WHERE ticket_no = ?', (ticket_no,))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total tickets
        cursor.execute('SELECT COUNT(*) FROM tickets')
        total_tickets = cursor.fetchone()[0]
        
        # Today's scans
        today_scans = self.get_today_scans()
        
        # Total entries today for this attraction
        # Normalize attraction name (handle both "A" and "AttractionA" formats)
        if self.attraction_name.startswith("Attraction"):
            attraction_short = self.attraction_name[-1]  # Get last character (A, B, or C)
        else:
            attraction_short = self.attraction_name.upper()
        
        attraction_col = f"{attraction_short}_used"
        cursor.execute(f'''
            SELECT SUM({attraction_col}) FROM tickets
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
        """Add sample tickets for testing with new format"""
        sample_tickets = [
            {
                "ticket_no": "20251009-000001",
                "booking_date": "2025-10-08",
                "reference_no": "20251009-000001",
                "attractions": {"A": {"pax": 2, "used": 0}, "B": {"pax": 0, "used": 0}, "C": {"pax": 0, "used": 0}}
            },
            {
                "ticket_no": "20251009-000002", 
                "booking_date": "2025-10-08",
                "reference_no": "20251009-000002",
                "attractions": {"A": {"pax": 1, "used": 0}, "B": {"pax": 0, "used": 0}, "C": {"pax": 0, "used": 0}}
            },
            {
                "ticket_no": "20251009-000003",
                "booking_date": "2025-10-08", 
                "reference_no": "20251009-000003",
                "attractions": {"A": {"pax": 3, "used": 0}, "B": {"pax": 3, "used": 0}, "C": {"pax": 0, "used": 0}}
            },
            {
                "ticket_no": "20251009-000004",
                "booking_date": "2025-10-08",
                "reference_no": "20251009-000004", 
                "attractions": {"A": {"pax": 4, "used": 0}, "B": {"pax": 4, "used": 0}, "C": {"pax": 4, "used": 0}}
            }
        ]
        
        for ticket_data in sample_tickets:
            self.add_ticket(
                ticket_data["ticket_no"],
                ticket_data["booking_date"], 
                ticket_data["reference_no"],
                ticket_data["attractions"]
            )
        
        print(f"Added {len(sample_tickets)} sample tickets to {self.attraction_name}")

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
