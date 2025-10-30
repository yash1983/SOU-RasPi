#!/usr/bin/env python3
"""
Performance Test for SOU Raspberry Pi
Tests database performance with large datasets
"""

import time
import random
from ticket_database import TicketDatabase

def test_database_performance(attraction_name, test_count=100):
    """Test database performance with random queries"""
    print(f"🧪 Performance Testing: {attraction_name}")
    print("=" * 50)
    
    # Initialize database
    db = TicketDatabase(attraction_name)
    
    # Get database statistics
    stats = db.get_stats()
    print(f"📊 Database Stats:")
    print(f"   Total tickets: {stats['total_tickets']:,}")
    print(f"   Unsynced records: {stats['unsynced_count']:,}")
    print()
    
    if stats['total_tickets'] == 0:
        print("❌ No tickets in database. Run add_test_tickets.py first.")
        return False
    
    # Test 1: Random ticket validation
    print("🔍 Test 1: Random Ticket Validation")
    print("-" * 30)
    
    validation_times = []
    
    for i in range(test_count):
        # Generate random ticket (might not exist)
        ticket_no = f"TICKET_C_{random.randint(1, 999):03d}_{random.randint(1, 6)}P_TEST"
        
        start_time = time.time()
        result = db.validate_ticket(ticket_no)
        end_time = time.time()
        
        validation_time = (end_time - start_time) * 1000  # Convert to ms
        validation_times.append(validation_time)
        
        if (i + 1) % 20 == 0:
            print(f"   Completed {i + 1}/{test_count} validations...")
    
    # Calculate statistics
    avg_validation = sum(validation_times) / len(validation_times)
    min_validation = min(validation_times)
    max_validation = max(validation_times)
    
    print(f"✅ Validation Performance:")
    print(f"   Average: {avg_validation:.2f}ms")
    print(f"   Minimum: {min_validation:.2f}ms")
    print(f"   Maximum: {max_validation:.2f}ms")
    print()
    
    # Test 2: Statistics retrieval
    print("📊 Test 2: Statistics Retrieval")
    print("-" * 30)
    
    stats_times = []
    
    for i in range(10):  # Fewer tests for stats
        start_time = time.time()
        stats = db.get_stats()
        end_time = time.time()
        
        stats_time = (end_time - start_time) * 1000
        stats_times.append(stats_time)
    
    avg_stats = sum(stats_times) / len(stats_times)
    min_stats = min(stats_times)
    max_stats = max(stats_times)
    
    print(f"✅ Statistics Performance:")
    print(f"   Average: {avg_stats:.2f}ms")
    print(f"   Minimum: {min_stats:.2f}ms")
    print(f"   Maximum: {max_stats:.2f}ms")
    print()
    
    # Test 3: Today's scans count
    print("📅 Test 3: Today's Scans Count")
    print("-" * 30)
    
    scan_times = []
    
    for i in range(10):
        start_time = time.time()
        today_scans = db.get_today_scans()
        end_time = time.time()
        
        scan_time = (end_time - start_time) * 1000
        scan_times.append(scan_time)
    
    avg_scan = sum(scan_times) / len(scan_times)
    min_scan = min(scan_times)
    max_scan = max(scan_times)
    
    print(f"✅ Today's Scans Performance:")
    print(f"   Average: {avg_scan:.2f}ms")
    print(f"   Minimum: {min_scan:.2f}ms")
    print(f"   Maximum: {max_scan:.2f}ms")
    print()
    
    # Overall performance summary
    print("🎯 Overall Performance Summary:")
    print("=" * 50)
    print(f"📊 Database size: {stats['total_tickets']:,} tickets")
    print(f"🔍 Validation queries: {avg_validation:.2f}ms average")
    print(f"📈 Statistics queries: {avg_stats:.2f}ms average")
    print(f"📅 Scan count queries: {avg_scan:.2f}ms average")
    
    # Performance rating
    if avg_validation < 50:
        rating = "🟢 Excellent"
    elif avg_validation < 100:
        rating = "🟡 Good"
    elif avg_validation < 200:
        rating = "🟠 Acceptable"
    else:
        rating = "🔴 Slow"
    
    print(f"🏆 Performance Rating: {rating}")
    
    return True

def main():
    """Main function"""
    print("🚀 SOU Raspberry Pi - Performance Test")
    print("=" * 60)
    
    attraction = "AttractionC"
    
    print(f"🎯 Testing: {attraction}")
    print("📊 This will test database performance with random queries")
    print()
    
    success = test_database_performance(attraction)
    
    if success:
        print("\n✅ Performance test completed!")
        print("\n💡 Tips for optimization:")
        print("   - Processing times < 50ms = Excellent")
        print("   - Processing times < 100ms = Good")
        print("   - Processing times < 200ms = Acceptable")
        print("   - Processing times > 200ms = Consider optimization")
    else:
        print("\n❌ Performance test failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())





