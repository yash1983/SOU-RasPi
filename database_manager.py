#!/usr/bin/env python3
"""
SQLite Database Manager for SOU Raspberry Pi
Optimized for 1GB RAM with 2 lakh records support
"""

import sqlite3
import time
import os
from datetime import datetime

class QRDatabase:
    def __init__(self, db_path="qr_scans.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database and tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create QR scans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qr_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qr_data TEXT NOT NULL,
                qr_type TEXT,
                scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                camera_index INTEGER,
                frame_saved TEXT
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_scan_time ON qr_scans(scan_time)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_qr_data ON qr_scans(qr_data)
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized: {self.db_path}")
    
    def add_scan(self, qr_data, qr_type, camera_index=0, frame_saved=None, max_records=1000):
        """Add a new QR scan to database and maintain max_records limit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert new scan
        cursor.execute('''
            INSERT INTO qr_scans (qr_data, qr_type, camera_index, frame_saved)
            VALUES (?, ?, ?, ?)
        ''', (qr_data, qr_type, camera_index, frame_saved))
        
        # Maintain record limit (keep only latest 1000 records)
        cursor.execute('''
            DELETE FROM qr_scans 
            WHERE id NOT IN (
                SELECT id FROM qr_scans 
                ORDER BY scan_time DESC 
                LIMIT ?
            )
        ''', (max_records,))
        
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            print(f"🗑️ Auto-cleanup: Removed {deleted_count} old records (keeping latest {max_records})")
        
        conn.commit()
        scan_id = cursor.lastrowid
        conn.close()
        
        return scan_id
    
    def get_recent_scans(self, limit=10):
        """Get recent QR scans"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, qr_data, qr_type, scan_time, frame_saved
            FROM qr_scans
            ORDER BY scan_time DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_scans(self, search_term):
        """Search QR scans by data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, qr_data, qr_type, scan_time, frame_saved
            FROM qr_scans
            WHERE qr_data LIKE ?
            ORDER BY scan_time DESC
            LIMIT 50
        ''', (f'%{search_term}%',))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total scans
        cursor.execute('SELECT COUNT(*) FROM qr_scans')
        total_scans = cursor.fetchone()[0]
        
        # Scans today
        cursor.execute('''
            SELECT COUNT(*) FROM qr_scans
            WHERE DATE(scan_time) = DATE('now')
        ''')
        today_scans = cursor.fetchone()[0]
        
        # Unique QR codes
        cursor.execute('SELECT COUNT(DISTINCT qr_data) FROM qr_scans')
        unique_codes = cursor.fetchone()[0]
        
        # Database size
        db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        conn.close()
        
        return {
            'total_scans': total_scans,
            'today_scans': today_scans,
            'unique_codes': unique_codes,
            'db_size_mb': round(db_size / (1024 * 1024), 2),
            'max_records': 1000,
            'records_used': total_scans
        }
    
    def set_record_limit(self, max_records=1000):
        """Manually set the maximum number of records to keep"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current count
        cursor.execute('SELECT COUNT(*) FROM qr_scans')
        current_count = cursor.fetchone()[0]
        
        if current_count > max_records:
            # Keep only the latest max_records
            cursor.execute('''
                DELETE FROM qr_scans 
                WHERE id NOT IN (
                    SELECT id FROM qr_scans 
                    ORDER BY scan_time DESC 
                    LIMIT ?
                )
            ''', (max_records,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"🗑️ Reduced database to {max_records} records (removed {deleted_count} old records)")
            return deleted_count
        else:
            conn.close()
            print(f"✅ Database already has {current_count} records (under limit of {max_records})")
            return 0
    
    def cleanup_old_scans(self, days=30):
        """Remove scans older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM qr_scans
            WHERE scan_time < datetime('now', '-{} days')
        '''.format(days))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"🗑️ Cleaned up {deleted_count} old scans (older than {days} days)")
        return deleted_count

def test_database():
    """Test database functionality"""
    print("🧪 Testing SQLite database...")
    
    db = QRDatabase("test_qr.db")
    
    # Add test scans
    print("📝 Adding test scans...")
    for i in range(5):
        db.add_scan(f"TEST_QR_CODE_{i}", "QRCODE", 0, f"test_frame_{i}.jpg")
    
    # Get stats
    stats = db.get_stats()
    print(f"📊 Database stats: {stats}")
    
    # Get recent scans
    recent = db.get_recent_scans(3)
    print(f"📋 Recent scans: {len(recent)} found")
    
    # Cleanup test database
    os.remove("test_qr.db")
    print("✅ Database test completed!")

if __name__ == "__main__":
    test_database()
