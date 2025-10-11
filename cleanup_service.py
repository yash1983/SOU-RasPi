#!/usr/bin/env python3
"""
Hourly Cleanup Service for SOU Raspberry Pi
Automatically cleans up old tickets and scan history every hour
"""

import sqlite3
import os
import time
import logging
import shutil
from datetime import datetime, timedelta
from config import config
from ticket_database import TicketDatabase

class CleanupService:
    """Hourly cleanup service for attraction databases"""
    
    def __init__(self):
        """Initialize cleanup service"""
        self.setup_logging()
        self.attractions = ["AttractionA", "AttractionB", "AttractionC"]
        self.databases = {}
        
        # Initialize databases for all attractions
        for attraction in self.attractions:
            self.databases[attraction] = TicketDatabase(attraction)
        
        self.logger.info("Hourly Cleanup Service initialized")
    
    def setup_logging(self):
        """Setup logging for the service"""
        logging.basicConfig(
            level=getattr(logging, config.get('logging.level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.get('logging.file', 'sou_system.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('HourlyCleanupService')
    
    def should_run_cleanup(self):
        """Check if cleanup should run (every hour)"""
        now = datetime.now()
        current_time = now.time()
        
        # Check if it's the top of the hour (00:00-00:05 minutes)
        # This ensures cleanup runs once per hour
        return current_time.minute <= 5
    
    def get_yesterday_date(self):
        """Get yesterday's date in YYYY-MM-DD format"""
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")
    
    def backup_database(self, db_path):
        """Create backup of database before cleanup"""
        try:
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"{os.path.basename(db_path)}_backup_{timestamp}")
            
            shutil.copy2(db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to backup database {db_path}: {e}")
            return None
    
    def cleanup_attraction_database(self, attraction_name):
        """Clean up a single attraction database"""
        db_path = f"{attraction_name}.db"
        
        if not os.path.exists(db_path):
            self.logger.warning(f"Database {db_path} not found, skipping...")
            return False
        
        try:
            # Create backup before cleanup
            backup_path = self.backup_database(db_path)
            if not backup_path:
                self.logger.error(f"Failed to backup {attraction_name}, skipping cleanup")
                return False
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get yesterday's date
            yesterday = self.get_yesterday_date()
            
            # Count records before cleanup
            cursor.execute('SELECT COUNT(*) FROM tickets')
            tickets_before = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM scan_history')
            scans_before = cursor.fetchone()[0]
            
            # Clean up old tickets (from yesterday and earlier)
            cursor.execute('''
                DELETE FROM tickets 
                WHERE booking_date <= ?
            ''', (yesterday,))
            tickets_deleted = cursor.rowcount
            
            # Clean up old scan history (from yesterday and earlier)
            cursor.execute('''
                DELETE FROM scan_history 
                WHERE DATE(scan_time) <= ?
            ''', (yesterday,))
            scans_deleted = cursor.rowcount
            
            # Reset auto-increment counter for scan_history
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="scan_history"')
            
            conn.commit()
            conn.close()
            
            # Vacuum database to reclaim space (must be done outside transaction)
            try:
                conn_vacuum = sqlite3.connect(db_path, timeout=5.0)
                cursor_vacuum = conn_vacuum.cursor()
                cursor_vacuum.execute('VACUUM')
                conn_vacuum.close()
                self.logger.info(f"   - Database vacuumed successfully")
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower():
                    self.logger.warning(f"   - Database locked (possibly by HeidiSQL), skipping vacuum")
                else:
                    self.logger.warning(f"   - Vacuum failed: {e}")
            except Exception as e:
                self.logger.warning(f"   - Vacuum failed: {e}")
            
            self.logger.info(f"[SUCCESS] {attraction_name} cleanup completed:")
            self.logger.info(f"   - Tickets before: {tickets_before}, deleted: {tickets_deleted}")
            self.logger.info(f"   - Scans before: {scans_before}, deleted: {scans_deleted}")
            self.logger.info(f"   - Backup created: {backup_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error cleaning up {attraction_name}: {e}")
            return False
    
    def cleanup_all_databases(self):
        """Clean up all attraction databases"""
        self.logger.info("[CLEANUP] Starting hourly cleanup of all databases...")
        
        success_count = 0
        total_count = len(self.attractions)
        
        for attraction in self.attractions:
            if self.cleanup_attraction_database(attraction):
                success_count += 1
        
        if success_count == total_count:
            self.logger.info(f"[SUCCESS] Hourly cleanup completed successfully for all {total_count} databases")
        else:
            self.logger.warning(f"[WARNING] Hourly cleanup completed with issues: {success_count}/{total_count} databases cleaned")
        
        return success_count == total_count
    
    def get_cleanup_stats(self):
        """Get statistics about database sizes before cleanup"""
        stats = {}
        
        for attraction in self.attractions:
            db_path = f"{attraction}.db"
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path, timeout=10.0)
                    cursor = conn.cursor()
                    
                    cursor.execute('SELECT COUNT(*) FROM tickets')
                    ticket_count = cursor.fetchone()[0]
                    
                    cursor.execute('SELECT COUNT(*) FROM scan_history')
                    scan_count = cursor.fetchone()[0]
                    
                    # Get database file size
                    file_size = os.path.getsize(db_path)
                    
                    conn.close()
                    
                    stats[attraction] = {
                        'tickets': ticket_count,
                        'scans': scan_count,
                        'file_size_mb': round(file_size / (1024 * 1024), 2)
                    }
                    
                except Exception as e:
                    self.logger.error(f"Error getting stats for {attraction}: {e}")
                    stats[attraction] = {'error': str(e)}
            else:
                stats[attraction] = {'error': 'Database not found'}
        
        return stats
    
    def run_cleanup_cycle(self):
        """Run a single cleanup cycle"""
        self.logger.info("[CLEANUP] Starting cleanup cycle...")
        
        # Get stats before cleanup
        stats_before = self.get_cleanup_stats()
        self.logger.info(f"Database stats before cleanup: {stats_before}")
        
        # Perform cleanup
        success = self.cleanup_all_databases()
        
        # Get stats after cleanup
        stats_after = self.get_cleanup_stats()
        self.logger.info(f"Database stats after cleanup: {stats_after}")
        
        return success
    
    def run(self):
        """Main service loop"""
        self.logger.info("[CLEANUP] Hourly Cleanup Service started")
        
        # Check interval (in seconds) - check every minute
        check_interval = 60
        
        while True:
            try:
                if self.should_run_cleanup():
                    self.logger.info("[CLEANUP] Hourly cleanup time detected")
                    self.run_cleanup_cycle()
                    
                    # Wait until after cleanup window to avoid multiple runs
                    self.logger.info("[CLEANUP] Waiting until after cleanup window...")
                    time.sleep(300)  # Wait 5 minutes
                else:
                    # Log current time and next cleanup time
                    now = datetime.now()
                    next_cleanup = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                    
                    time_until_cleanup = next_cleanup - now
                    self.logger.debug(f"Next cleanup in {time_until_cleanup}")
                
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("[CLEANUP] Hourly Cleanup Service stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in cleanup service: {e}")
                time.sleep(check_interval)

def main():
    """Main entry point for hourly cleanup service"""
    service = CleanupService()
    service.run()

if __name__ == "__main__":
    main()
