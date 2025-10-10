#!/usr/bin/env python3
"""
Debug script to help diagnose sync issues on the Raspberry Pi
Run this on the Pi to check the sync status of tickets
"""

import sqlite3
from ticket_database import TicketDatabase

def debug_ticket_sync_status(ticket_no):
    """Debug the sync status of a specific ticket"""
    print(f"=== Debugging ticket: {ticket_no} ===")
    
    attractions = ["AttractionA", "AttractionB", "AttractionC"]
    
    for attraction in attractions:
        print(f"\n--- {attraction} ---")
        db = TicketDatabase(attraction)
        
        # Check if ticket exists
        exists = db.ticket_exists(ticket_no)
        print(f"Ticket exists: {exists}")
        
        if exists:
            # Get ticket info
            info = db.get_ticket_info(ticket_no)
            print(f"Ticket info: {info}")
            
            # Get sync debug info
            debug_info = db.get_sync_debug_info(ticket_no)
            print(f"Sync debug info: {debug_info}")
            
            # Try to mark as synced and see what happens
            print(f"Attempting to mark as synced...")
            result = db.mark_ticket_synced(ticket_no)
            print(f"Mark as synced result: {result}")
            
            # Check status after marking
            info_after = db.get_ticket_info(ticket_no)
            print(f"Ticket info after marking: {info_after}")

def check_all_unsynced_tickets():
    """Check all unsynced tickets across all databases"""
    print("=== All Unsynced Tickets ===")
    
    attractions = ["AttractionA", "AttractionB", "AttractionC"]
    
    for attraction in attractions:
        print(f"\n--- {attraction} ---")
        db = TicketDatabase(attraction)
        
        # Get unsynced tickets
        unsynced = db.get_unsynced_tickets()
        print(f"Unsynced tickets: {unsynced}")
        
        # Get stats
        stats = db.get_stats()
        print(f"Database stats: {stats}")

def test_mark_synced_functionality():
    """Test the mark_synced functionality"""
    print("=== Testing Mark Synced Functionality ===")
    
    # Test with a known ticket
    test_ticket = "20251010-000006"
    
    attractions = ["AttractionA", "AttractionB", "AttractionC"]
    
    for attraction in attractions:
        print(f"\n--- Testing {attraction} ---")
        db = TicketDatabase(attraction)
        
        if db.ticket_exists(test_ticket):
            print(f"Found ticket {test_ticket} in {attraction}")
            
            # Get current status
            info = db.get_ticket_info(test_ticket)
            print(f"Current is_synced: {info['is_synced'] if info else 'N/A'}")
            
            # Try to mark as synced
            result = db.mark_ticket_synced(test_ticket)
            print(f"Mark synced result: {result}")
            
            # Check status after
            info_after = db.get_ticket_info(test_ticket)
            print(f"After marking is_synced: {info_after['is_synced'] if info_after else 'N/A'}")
        else:
            print(f"Ticket {test_ticket} not found in {attraction}")

if __name__ == "__main__":
    print("🔍 SOU Sync Issue Debug Tool")
    print("=" * 50)
    
    # Check specific ticket
    debug_ticket_sync_status("20251010-000006")
    
    print("\n" + "=" * 50)
    
    # Check all unsynced tickets
    check_all_unsynced_tickets()
    
    print("\n" + "=" * 50)
    
    # Test mark synced functionality
    test_mark_synced_functionality()
    
    print("\n✅ Debug complete!")
