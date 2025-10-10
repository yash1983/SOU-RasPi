#!/usr/bin/env python3
"""
Sync Service for SOU Raspberry Pi
Background service to sync unsynced records back to server
"""

import requests
import json
import time
import logging
from datetime import datetime
from config import config
from ticket_database import TicketDatabase

class SyncService:
    """Background service to sync unsynced records to server"""
    
    def __init__(self):
        """Initialize sync service"""
        self.setup_logging()
        self.attractions = ["AttractionA", "AttractionB", "AttractionC"]
        self.databases = {}
        
        # Initialize databases for all attractions
        for attraction in self.attractions:
            self.databases[attraction] = TicketDatabase(attraction)
        
        self.logger.info("Sync Service initialized")
    
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
        self.logger = logging.getLogger('SyncService')
    
    def sync_ticket_to_server(self, ticket_no, ticket_data):
        """Sync a single ticket to server"""
        try:
            url = config.get_sync_url()
            timeout = config.get('api.timeout', 30)
            retry_attempts = config.get('api.retry_attempts', 3)
            retry_delay = config.get('api.retry_delay', 5)
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            for attempt in range(retry_attempts):
                try:
                    self.logger.info(f"Syncing ticket {ticket_no} to server (attempt {attempt + 1}/{retry_attempts})")
                    self.logger.info(f"Sending data: {ticket_data}")
                    
                    response = requests.post(
                        url, 
                        json=ticket_data, 
                        headers=headers, 
                        timeout=timeout
                    )
                    
                    self.logger.info(f"Server response: {response.status_code} - {response.text[:200]}")
                    response.raise_for_status()
                    
                    self.logger.info(f"Successfully synced ticket {ticket_no} to server")
                    return True
                    
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed for ticket {ticket_no}: {e}")
                    if attempt < retry_attempts - 1:
                        self.logger.info(f"Waiting {retry_delay} seconds before retry")
                        time.sleep(retry_delay)
                    else:
                        self.logger.error(f"All attempts failed for ticket {ticket_no}")
                        return False
            
        except Exception as e:
            self.logger.error(f"Unexpected error syncing ticket {ticket_no}: {e}")
            return False
    
    def get_all_unsynced_tickets(self):
        """Get all unsynced tickets from all attraction databases"""
        all_unsynced = {}
        
        for attraction in self.attractions:
            db = self.databases[attraction]
            unsynced_tickets = db.get_unsynced_tickets()
            
            for ticket_no in unsynced_tickets:
                # Skip dummy tickets if configured to do so
                if config.get('services.skip_dummy_sync', True) and ticket_no.endswith('-dummy'):
                    self.logger.debug(f"Skipping dummy ticket: {ticket_no}")
                    continue
                    
                if ticket_no not in all_unsynced:
                    # Get ticket data from the first database that has it
                    ticket_data = db.get_ticket_for_sync(ticket_no)
                    if ticket_data:
                        all_unsynced[ticket_no] = ticket_data
        
        return all_unsynced
    
    def sync_unsynced_tickets(self):
        """Sync all unsynced tickets to server"""
        unsynced_tickets = self.get_all_unsynced_tickets()
        
        if not unsynced_tickets:
            self.logger.info("No unsynced tickets found")
            return 0
        
        self.logger.info(f"Found {len(unsynced_tickets)} unsynced tickets")
        
        synced_count = 0
        failed_count = 0
        
        for ticket_no, ticket_data in unsynced_tickets.items():
            if self.sync_ticket_to_server(ticket_no, ticket_data):
                # Mark as synced in all databases that have this ticket
                marked_count = 0
                for attraction in self.attractions:
                    db = self.databases[attraction]
                    if db.ticket_exists(ticket_no):
                        try:
                            result = db.mark_ticket_synced(ticket_no)
                            if result:
                                marked_count += 1
                                self.logger.info(f"Marked ticket {ticket_no} as synced in {attraction}")
                            else:
                                self.logger.warning(f"Failed to mark ticket {ticket_no} as synced in {attraction}")
                        except Exception as e:
                            self.logger.error(f"Error marking ticket {ticket_no} as synced in {attraction}: {e}")
                
                if marked_count > 0:
                    self.logger.info(f"Successfully marked ticket {ticket_no} as synced in {marked_count} database(s)")
                    synced_count += 1
                else:
                    self.logger.error(f"Failed to mark ticket {ticket_no} as synced in any database")
                    failed_count += 1
            else:
                failed_count += 1
        
        self.logger.info(f"Sync completed: {synced_count} synced, {failed_count} failed")
        return synced_count
    
    def run_sync_cycle(self):
        """Run a single sync cycle"""
        self.logger.info("Starting sync cycle")
        
        synced_count = self.sync_unsynced_tickets()
        
        self.logger.info("Sync cycle completed")
        return synced_count
    
    def run(self):
        """Main service loop"""
        self.logger.info("Sync Service started")
        
        sync_interval = config.get('services.sync_interval', 1)  # 1 second default
        
        while True:
            try:
                if config.get('services.sync_enabled', True):
                    synced_count = self.run_sync_cycle()
                    
                    # If no tickets were synced, wait the full interval
                    # If tickets were synced, wait 1 second as specified
                    if synced_count == 0:
                        self.logger.info(f"No tickets to sync, waiting {sync_interval} seconds")
                        time.sleep(sync_interval)
                    else:
                        self.logger.info("Tickets synced, waiting 1 second")
                        time.sleep(1)
                else:
                    self.logger.info("Sync service is disabled in configuration")
                    time.sleep(sync_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Sync Service stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in sync service: {e}")
                self.logger.info("Waiting 5 seconds before retry")
                time.sleep(5)

def main():
    """Main entry point for sync service"""
    service = SyncService()
    service.run()

if __name__ == "__main__":
    main()
