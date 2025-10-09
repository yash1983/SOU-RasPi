#!/usr/bin/env python3
"""
Add Test Tickets for Performance Testing
Adds 100,000 random tickets to Attraction C database
"""

import random
import string
import time
from ticket_database import TicketDatabase

def generate_random_ticket():
    """Generate a random ticket number"""
    # Generate random ticket types
    ticket_types = ["TICKET_C", "TICKET_ABC"]
    
    # Random ticket type
    ticket_type = random.choice(ticket_types)
    
    # Random 3-digit number
    ticket_num = f"{random.randint(1, 999):03d}"
    
    # Random person count (1-6 people)
    person_count = random.randint(1, 6)
    
    # Random suffix
    suffix = ''.join(random.choices(string.ascii_uppercase, k=2))
    
    return f"{ticket_type}_{ticket_num}_{person_count}P_{suffix}"

def add_test_tickets(attraction_name, count=100000):
    """Add test tickets to specified attraction database"""
    print(f"🎫 Adding {count:,} test tickets to {attraction_name}")
    print("=" * 60)
    
    # Initialize database
    db = TicketDatabase(attraction_name)
    
    # Start timing
    start_time = time.time()
    
    # Generate and add tickets in batches for better performance
    batch_size = 1000
    total_batches = count // batch_size
    remaining = count % batch_size
    
    print(f"📦 Processing {total_batches} batches of {batch_size} tickets each")
    if remaining > 0:
        print(f"📦 Plus 1 batch of {remaining} tickets")
    
    tickets_added = 0
    
    try:
        for batch_num in range(total_batches):
            batch_start = time.time()
            
            # Generate batch of tickets
            batch_tickets = []
            for i in range(batch_size):
                ticket_no = generate_random_ticket()
                persons_allowed = random.randint(1, 6)
                batch_tickets.append((ticket_no, persons_allowed))
            
            # Add batch to database using bulk insert
            success = db.add_tickets_bulk(batch_tickets)
            if success:
                tickets_added += len(batch_tickets)
            else:
                print(f"❌ Failed to add batch {batch_num + 1}")
                break
            
            batch_time = time.time() - batch_start
            batch_rate = batch_size / batch_time
            
            print(f"✅ Batch {batch_num + 1}/{total_batches}: {batch_size} tickets in {batch_time:.2f}s ({batch_rate:.1f} tickets/sec)")
        
        # Add remaining tickets if any
        if remaining > 0:
            batch_start = time.time()
            
            # Generate remaining tickets
            remaining_tickets = []
            for i in range(remaining):
                ticket_no = generate_random_ticket()
                persons_allowed = random.randint(1, 6)
                remaining_tickets.append((ticket_no, persons_allowed))
            
            # Add remaining tickets using bulk insert
            success = db.add_tickets_bulk(remaining_tickets)
            if success:
                tickets_added += len(remaining_tickets)
            
            batch_time = time.time() - batch_start
            batch_rate = remaining / batch_time
            
            print(f"✅ Final batch: {remaining} tickets in {batch_time:.2f}s ({batch_rate:.1f} tickets/sec)")
        
        # Calculate total statistics
        total_time = time.time() - start_time
        avg_rate = tickets_added / total_time
        
        print("\n" + "=" * 60)
        print("📊 Performance Summary:")
        print(f"   Total tickets added: {tickets_added:,}")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Average rate: {avg_rate:.1f} tickets/second")
        print(f"   Database: {attraction_name}.db")
        
        # Get final database statistics
        stats = db.get_stats()
        print(f"\n📋 Database Statistics:")
        print(f"   Total tickets: {stats['total_tickets']:,}")
        print(f"   Unsynced records: {stats['unsynced_count']:,}")
        print(f"   Today's scans: {stats['today_scans']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding tickets: {e}")
        return False

def main():
    """Main function"""
    print("🚀 SOU Raspberry Pi - Test Ticket Generator")
    print("=" * 60)
    
    attraction = "AttractionC"
    ticket_count = 100000
    
    print(f"🎯 Target: {attraction}")
    print(f"📊 Tickets to add: {ticket_count:,}")
    print()
    
    # Confirm before proceeding
    confirm = input(f"⚠️  This will add {ticket_count:,} tickets to {attraction}. Continue? (y/N): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Operation cancelled")
        return 1
    
    # Add tickets
    success = add_test_tickets(attraction, ticket_count)
    
    if success:
        print("\n🎉 Test tickets added successfully!")
        print("\n🧪 You can now test performance with:")
        print(f"   python3 {attraction}.py")
        print("\n📊 Monitor processing times to see database performance impact")
        return 0
    else:
        print("\n❌ Failed to add test tickets!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

