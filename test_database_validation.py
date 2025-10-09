#!/usr/bin/env python3
"""
Test Database-Based Validation System
Tests the new attraction validation that works with any QR format
"""

from ticket_database import TicketDatabase

def test_database_validation():
    """Test the new database-based validation system"""
    print("🧪 Testing Database-Based Attraction Validation")
    print("=" * 60)
    
    # Initialize database for Attraction A
    db_a = TicketDatabase("AttractionA")
    
    # Add sample tickets with different attraction combinations
    sample_tickets = [
        ("QR123456789", 2, "A"),           # Valid only for Attraction A
        ("QR987654321", 3, "A,B"),         # Valid for Attraction A & B
        ("QR555666777", 4, "A,B,C"),       # Valid for all attractions
        ("QR111222333", 1, "B"),           # Valid only for Attraction B
        ("QR444555666", 2, "C"),           # Valid only for Attraction C
    ]
    
    print("📝 Adding test tickets with various attraction combinations...")
    for ticket_no, persons, attractions in sample_tickets:
        db_a.add_ticket(ticket_no, persons, attractions)
        print(f"   ✅ {ticket_no}: {persons} persons, valid for {attractions}")
    
    print("\n🔍 Testing validation from Attraction A perspective:")
    print("-" * 50)
    
    # Test validation from Attraction A
    test_cases = [
        ("QR123456789", "Should be valid (A only)"),
        ("QR987654321", "Should be valid (A,B)"),
        ("QR555666777", "Should be valid (A,B,C)"),
        ("QR111222333", "Should be invalid (B only)"),
        ("QR444555666", "Should be invalid (C only)"),
        ("QR999888777", "Should be invalid (not found)"),
    ]
    
    for ticket_no, description in test_cases:
        result = db_a.validate_and_log_ticket(ticket_no, "A")
        status = "✅ Valid" if result['valid'] else "❌ Invalid"
        print(f"   {status} {ticket_no}: {result['reason']} - {description}")
    
    print("\n🔍 Testing validation from Attraction B perspective:")
    print("-" * 50)
    
    # Test validation from Attraction B
    db_b = TicketDatabase("AttractionB")
    for ticket_no, persons, attractions in sample_tickets:
        db_b.add_ticket(ticket_no, persons, attractions)
    
    for ticket_no, description in test_cases:
        result = db_b.validate_and_log_ticket(ticket_no, "B")
        status = "✅ Valid" if result['valid'] else "❌ Invalid"
        print(f"   {status} {ticket_no}: {result['reason']} - {description}")
    
    print("\n🔍 Testing validation from Attraction C perspective:")
    print("-" * 50)
    
    # Test validation from Attraction C
    db_c = TicketDatabase("AttractionC")
    for ticket_no, persons, attractions in sample_tickets:
        db_c.add_ticket(ticket_no, persons, attractions)
    
    for ticket_no, description in test_cases:
        result = db_c.validate_and_log_ticket(ticket_no, "C")
        status = "✅ Valid" if result['valid'] else "❌ Invalid"
        print(f"   {status} {ticket_no}: {result['reason']} - {description}")
    
    print("\n" + "=" * 60)
    print("🎯 Key Benefits of Database-Based Validation:")
    print("   • Works with ANY QR format (no text pattern matching)")
    print("   • Flexible attraction combinations (A, B, C, A,B, A,C, B,C, A,B,C)")
    print("   • Easy to update ticket validity without code changes")
    print("   • Ready for live data with different QR formats")
    print("   • Single source of truth in database")
    
    print("\n💡 Example for Live Data:")
    print("   • QR Code: 'LIVE123456789'")
    print("   • Attractions: 'A,B,C' (valid for all)")
    print("   • No code changes needed - just database update!")

if __name__ == "__main__":
    test_database_validation()
