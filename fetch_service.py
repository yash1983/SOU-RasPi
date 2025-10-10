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
        
        # Log configuration for debugging
        self.log_configuration()
        
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
    
    def log_configuration(self):
        """Log current configuration for debugging"""
        self.logger.info("=== Fetch Service Configuration ===")
        self.logger.info(f"Base URL: {config.get('api.base_url')}")
        self.logger.info(f"Fetch URL: {config.get_fetch_url()}")
        self.logger.info(f"Timeout: {config.get('api.timeout', 30)} seconds")
        self.logger.info(f"Retry Attempts: {config.get('api.retry_attempts', 3)}")
        self.logger.info(f"Retry Delay: {config.get('api.retry_delay', 5)} seconds")
        self.logger.info(f"Fetch Interval: {config.get('services.fetch_interval', 300)} seconds")
        self.logger.info(f"Fetch Enabled: {config.get('services.fetch_enabled', True)}")
        self.logger.info("=====================================")
    
    def fetch_tickets_from_server(self):
        """Fetch tickets from server API with retry logic"""
        url = config.get_fetch_url()
        timeout = config.get('api.timeout', 30)
        retry_attempts = config.get('api.retry_attempts', 3)
        retry_delay = config.get('api.retry_delay', 5)
        
        self.logger.info(f"Fetching tickets from: {url}")
        
        for attempt in range(retry_attempts):
            try:
                # Create session with connection pooling and keep-alive
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'SOU-RasPi-FetchService/1.0',
                    'Connection': 'keep-alive',
                    'Accept': 'application/json'
                })
                
                # Configure connection adapter with retry strategy
                from requests.adapters import HTTPAdapter
                from urllib3.util.retry import Retry
                
                retry_strategy = Retry(
                    total=2,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["HEAD", "GET", "OPTIONS"]
                )
                
                adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=1, pool_maxsize=1)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                
                response = session.get(url, timeout=timeout)
                response.raise_for_status()
                
                tickets_data = response.json()
                self.logger.info(f"Fetched {len(tickets_data)} tickets from server")
                
                return tickets_data
                
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"Connection error (attempt {attempt + 1}/{retry_attempts}): {e}")
                if attempt < retry_attempts - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"Failed to connect after {retry_attempts} attempts")
                    
            except requests.exceptions.Timeout as e:
                self.logger.warning(f"Timeout error (attempt {attempt + 1}/{retry_attempts}): {e}")
                if attempt < retry_attempts - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"Request timed out after {retry_attempts} attempts")
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error (attempt {attempt + 1}/{retry_attempts}): {e}")
                if attempt < retry_attempts - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"Request failed after {retry_attempts} attempts")
                    
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing JSON response: {e}")
                return None
                
            except Exception as e:
                self.logger.error(f"Unexpected error fetching tickets: {e}")
                return None
        
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
                        # Update existing ticket (smart update: only increases used counts)
                        success = db.add_ticket(ticket_no, booking_date, ticket_no, attractions_data)
                        if success:
                            updated_count += 1
                            self.logger.debug(f"Updated ticket {ticket_no} in {attraction} (smart update: used counts only increase)")
                        else:
                            self.logger.error(f"Failed to update ticket {ticket_no} in {attraction}")
                    else:
                        # Create new ticket
                        success = db.add_ticket(ticket_no, booking_date, ticket_no, attractions_data)
                        if success:
                            created_count += 1
                            self.logger.debug(f"Created new ticket {ticket_no} in {attraction}")
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
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        while True:
            try:
                if config.get('services.fetch_enabled', True):
                    self.run_fetch_cycle()
                    consecutive_failures = 0  # Reset failure counter on success
                else:
                    self.logger.info("Fetch service is disabled in configuration")
                
                # Wait for next cycle
                self.logger.info(f"Waiting {fetch_interval} seconds for next fetch cycle")
                time.sleep(fetch_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Fetch Service stopped by user")
                break
            except Exception as e:
                consecutive_failures += 1
                self.logger.error(f"Unexpected error in fetch service (failure #{consecutive_failures}): {e}")
                
                if consecutive_failures >= max_consecutive_failures:
                    self.logger.error(f"Too many consecutive failures ({consecutive_failures}). Increasing wait time.")
                    wait_time = min(300, 60 * consecutive_failures)  # Max 5 minutes
                else:
                    wait_time = 60
                
                self.logger.info(f"Waiting {wait_time} seconds before retry")
                time.sleep(wait_time)

def main():
    """Main entry point for fetch service"""
    service = FetchService()
    service.run()

if __name__ == "__main__":
    main()
