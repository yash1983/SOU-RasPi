#!/usr/bin/env python3
"""
Fetch Service for SOU Raspberry Pi
Background service to fetch tickets from server and create local records
"""

import requests
import json
import time
import logging
from datetime import datetime
from config import config
from ticket_database import TicketDatabase

class FetchService:
    """Background service to fetch tickets from server"""
    
    def __init__(self):
        """Initialize fetch service"""
        self.setup_logging()
        self.attractions = ["AttractionA", "AttractionB", "AttractionC"]
        self.databases = {}
        
        # Initialize databases for all attractions
        for attraction in self.attractions:
            self.databases[attraction] = TicketDatabase(attraction)
        
        self.logger.info("Fetch Service initialized")
    
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
        self.logger = logging.getLogger('FetchService')
    
    def fetch_tickets_from_server(self):
        """Fetch tickets from server API"""
        try:
            url = config.get_fetch_url()
            timeout = config.get('api.timeout', 30)
            
            self.logger.info(f"Fetching tickets from: {url}")
            
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            tickets_data = response.json()
            self.logger.info(f"Fetched {len(tickets_data)} tickets from server")
            
            return tickets_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching tickets from server: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON response: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching tickets: {e}")
            return None
    
    def process_tickets(self, tickets_data):
        """Process fetched tickets and create/update local records"""
        if not tickets_data:
            return
        
        processed_count = 0
        created_count = 0
        updated_count = 0
        skipped_count = 0
        today = datetime.now().strftime("%Y-%m-%d")
        
        for ticket_data in tickets_data:
            try:
                # Extract ticket information (handle both camelCase and PascalCase)
                ticket_no = ticket_data.get("ReferenceNo") or ticket_data.get("referenceNo")
                booking_date = ticket_data.get("BookingDate") or ticket_data.get("bookingDate")
                attractions_data = ticket_data.get("Attractions", {}) or ticket_data.get("attractions", {})
                
                if not ticket_no or not booking_date or not attractions_data:
                    self.logger.warning(f"⚠️  Skipping invalid ticket data: {ticket_data}")
                    continue
                
                # Only process tickets for today's date
                if booking_date != today:
                    self.logger.debug(f"Skipping ticket {ticket_no} - not for today (booking_date: {booking_date}, today: {today})")
                    skipped_count += 1
                    continue
                
                # Process for each attraction database
                for attraction in self.attractions:
                    db = self.databases[attraction]
                    
                    # Check if ticket already exists
                    if db.ticket_exists(ticket_no):
                        # Update existing ticket
                        success = db.add_ticket(ticket_no, booking_date, ticket_no, attractions_data)
                        if success:
                            updated_count += 1
                        else:
                            self.logger.error(f"Failed to update ticket {ticket_no} in {attraction}")
                    else:
                        # Create new ticket
                        success = db.add_ticket(ticket_no, booking_date, ticket_no, attractions_data)
                        if success:
                            created_count += 1
                        else:
                            self.logger.error(f"Failed to create ticket {ticket_no} in {attraction}")
                
                processed_count += 1
                
            except Exception as e:
                self.logger.error(f"Error processing ticket {ticket_data}: {e}")
        
        self.logger.info(f"Processed {processed_count} tickets: {created_count} created, {updated_count} updated, {skipped_count} skipped (not today's date)")
    
    def run_fetch_cycle(self):
        """Run a single fetch cycle"""
        self.logger.info("Starting fetch cycle")
        
        # Fetch tickets from server
        tickets_data = self.fetch_tickets_from_server()
        
        if tickets_data:
            # Process and store tickets
            self.process_tickets(tickets_data)
        else:
            self.logger.warning("No tickets fetched, skipping processing")
        
        self.logger.info("Fetch cycle completed")
    
    def run(self):
        """Main service loop"""
        self.logger.info("Fetch Service started")
        
        fetch_interval = config.get('services.fetch_interval', 300)  # 5 minutes default
        
        while True:
            try:
                if config.get('services.fetch_enabled', True):
                    self.run_fetch_cycle()
                else:
                    self.logger.info("Fetch service is disabled in configuration")
                
                # Wait for next cycle
                self.logger.info(f"Waiting {fetch_interval} seconds for next fetch cycle")
                time.sleep(fetch_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Fetch Service stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in fetch service: {e}")
                self.logger.info("Waiting 60 seconds before retry")
                time.sleep(60)

def main():
    """Main entry point for fetch service"""
    service = FetchService()
    service.run()

if __name__ == "__main__":
    main()
