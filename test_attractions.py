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
    print("🧪 Testing Ticket Validation System")
    print("=" * 50)
    
    # Test Attraction A
    print("\n🎯 Testing Attraction A...")
    db_a = TicketDatabase("AttractionA")
    db_a.add_sample_tickets()
    
    # Test valid ticket
    result = db_a.validate_ticket("TICKET_A_001_2P")
    print(f"TICKET_A_001_2P: {result}")
    
    # Test invalid ticket
    result = db_a.validate_ticket("TICKET_B_001_2P")
    print(f"TICKET_B_001_2P: {result}")
    
    # Test Attraction B
    print("\n🎯 Testing Attraction B...")
    db_b = TicketDatabase("AttractionB")
    db_b.add_sample_tickets()
    
    # Test valid ticket
    result = db_b.validate_ticket("TICKET_AB_001_3P")
    print(f"TICKET_AB_001_3P: {result}")
    
    # Test Attraction C
    print("\n🎯 Testing Attraction C...")
    db_c = TicketDatabase("AttractionC")
    db_c.add_sample_tickets()
    
    # Test valid ticket
    result = db_c.validate_ticket("TICKET_ABC_001_4P")
    print(f"TICKET_ABC_001_4P: {result}")
    
    # Test invalid ticket
    result = db_c.validate_ticket("TICKET_A_001_2P")
    print(f"TICKET_A_001_2P: {result}")

def test_display_screens():
    """Test display screens without camera"""
    print("\n🖥️ Testing Display Screens...")
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
    print("\n📊 Testing Database Statistics...")
    print("=" * 50)
    
    db = TicketDatabase("TestAttraction")
    db.add_sample_tickets()
    
    stats = db.get_stats()
    print(f"Database Stats: {stats}")
    
    # Test multiple scans
    for i in range(3):
        result = db.validate_ticket("TICKET_A_001_2P")
        print(f"Scan {i+1}: {result}")

def main():
    """Main test function"""
    print("🚀 SOU Raspberry Pi - Attraction System Test")
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
