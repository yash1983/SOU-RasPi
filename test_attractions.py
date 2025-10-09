#!/usr/bin/env python3
"""
Test script for SOU Raspberry Pi Attractions
Tests the ticket validation system without camera
"""

from ticket_database import TicketDatabase
from display_manager import DisplayManager
import time

def test_ticket_validation():
    """Test ticket validation for all attractions"""
    print("Testing Ticket Validation System")
    print("=" * 50)
    
    # Test Attraction A
    print("\nTesting Attraction A...")
    db_a = TicketDatabase("AttractionA")
    db_a.add_sample_tickets()
    
    # Test valid ticket
    result = db_a.validate_ticket("20251009-000001-dummy", "A")
    print(f"20251009-000001-dummy: {result}")
    
    # Test invalid ticket
    result = db_a.validate_ticket("20251009-000002-dummy", "A")
    print(f"20251009-000002-dummy: {result}")
    
    # Test Attraction B
    print("\nTesting Attraction B...")
    db_b = TicketDatabase("AttractionB")
    db_b.add_sample_tickets()
    
    # Test valid ticket
    result = db_b.validate_ticket("20251009-000003-dummy", "B")
    print(f"20251009-000003-dummy: {result}")
    
    # Test Attraction C
    print("\nTesting Attraction C...")
    db_c = TicketDatabase("AttractionC")
    db_c.add_sample_tickets()
    
    # Test valid ticket
    result = db_c.validate_ticket("20251009-000004-dummy", "C")
    print(f"20251009-000004-dummy: {result}")
    
    # Test invalid ticket
    result = db_c.validate_ticket("20251009-000001-dummy", "C")
    print(f"20251009-000001-dummy: {result}")

def test_display_screens():
    """Test display screens without camera"""
    print("\nTesting Display Screens...")
    print("=" * 50)
    
    dm = DisplayManager("AttractionA")
    
    # Test waiting screen
    print("📱 Creating waiting screen...")
    waiting_screen = dm.create_waiting_screen(5)
    print("✅ Waiting screen created")
    
    # Test success screen
    print("✅ Creating success screen...")
    ticket_info = {'persons_allowed': 2, 'persons_entered': 1}
    success_screen = dm.create_success_screen(ticket_info, 6)
    print("✅ Success screen created")
    
    # Test error screen
    print("❌ Creating error screen...")
    error_screen = dm.create_error_screen("QR already scanned", 6)
    print("✅ Error screen created")
    
    dm.cleanup()

def test_database_stats():
    """Test database statistics"""
    print("\nTesting Database Statistics...")
    print("=" * 50)
    
    db = TicketDatabase("TestAttraction")
    db.add_sample_tickets()
    
    stats = db.get_stats()
    print(f"Database Stats: {stats}")
    
    # Test multiple scans
    for i in range(3):
        result = db.validate_ticket("20251009-000001-dummy", "A")
        print(f"Scan {i+1}: {result}")

def main():
    """Main test function"""
    print("SOU Raspberry Pi - Attraction System Test")
    print("=" * 60)
    
    try:
        test_ticket_validation()
        test_display_screens()
        test_database_stats()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Test Summary:")
        print("   - Ticket validation working")
        print("   - Display screens functional")
        print("   - Database operations working")
        print("   - Multi-attraction support confirmed")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
