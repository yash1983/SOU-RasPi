# SOU Raspberry Pi - Attraction QR Scanner System

This system demonstrates how a Raspberry Pi can act as a controller for turnstile/flap barrier systems using QR code scanning for ticket validation.

## Features

- **Three Attractions**: Separate scanners for Attraction A, B, and C
- **Fullscreen Display**: Professional fullscreen interface with status information
- **QR Code Validation**: Real-time QR code scanning with USB camera
- **Local Database**: SQLite database for offline operation
- **Multi-person Tickets**: Support for tickets with multiple entries
- **Scan Cooldown**: 3-second cooldown to prevent duplicate scans
- **Online/Offline Status**: Displays internet connection status
- **Visual Feedback**: Green tick for valid entries, red X for invalid entries

## Files Structure

```
├── AttractionA.py          # Main application for Gate A
├── AttractionB.py          # Main application for Gate B  
├── AttractionC.py          # Main application for Gate C
├── ticket_database.py      # Database manager for ticket validation
├── display_manager.py      # Fullscreen display management
├── test_attractions.py     # Test script (no camera required)
└── requirements.txt        # Python dependencies
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install system dependencies (Raspberry Pi):
```bash
sudo apt-get update
sudo apt-get install python3-opencv libzbar0
```

## Usage

### Running Individual Attractions

**Attraction A:**
```bash
python3 AttractionA.py
```

**Attraction B:**
```bash
python3 AttractionB.py
```

**Attraction C:**
```bash
python3 AttractionC.py
```

### Testing (No Camera Required)

```bash
python3 test_attractions.py
```

## Ticket Format

The system uses the following ticket naming convention:

- `TICKET_A_XXX_XP` - Valid for Attraction A only
- `TICKET_B_XXX_XP` - Valid for Attraction B only  
- `TICKET_C_XXX_XP` - Valid for Attraction C only
- `TICKET_AB_XXX_XP` - Valid for Attraction A and B
- `TICKET_ABC_XXX_XP` - Valid for all attractions

Where:
- `XXX` = Ticket number
- `XP` = Number of persons (e.g., 2P = 2 persons)

## Sample Tickets

The system automatically creates sample tickets for testing:

- `20251009-000001-dummy` - 2 persons for Attraction A
- `20251009-000002-dummy` - 1 person for Attraction A
- `20251009-000003-dummy` - 3 persons for Attraction A & B
- `20251009-000004-dummy` - 4 persons for all attractions

## Controls

- **q** - Quit application
- **r** - Reset scan cooldown
- **s** - Show statistics

## Display Information

The fullscreen display shows:

- Attraction name
- "Waiting for QR code..." message
- Current date and time
- Today's scan count
- Online/Offline status
- Validation results (Valid Entry / Entry Not Valid)

## Database

Each attraction has its own SQLite database:

- `AttractionA.db` - Tickets for Attraction A
- `AttractionB.db` - Tickets for Attraction B
- `AttractionC.db` - Tickets for Attraction C

### Database Schema

**tickets table:**
- `ticket_no` (TEXT) - 30-character ticket identifier
- `persons_allowed` (INTEGER) - Number of persons allowed
- `persons_entered` (INTEGER) - Number of persons who entered
- `is_synced` (BOOLEAN) - Sync status with server
- `created_at` (TIMESTAMP) - Ticket creation time
- `last_scan` (TIMESTAMP) - Last scan time

**scan_history table:**
- `id` (INTEGER) - Auto-increment ID
- `ticket_no` (TEXT) - Ticket identifier
- `scan_time` (TIMESTAMP) - Scan timestamp
- `result` (TEXT) - SUCCESS/FAILED
- `reason` (TEXT) - Reason for result

## Validation Logic

1. **Attraction Check**: Verify ticket is valid for current attraction
2. **Database Lookup**: Check if ticket exists in local database
3. **Entry Limit**: Ensure not all entries have been used
4. **Update Count**: Increment persons_entered counter
5. **Log Result**: Record scan attempt in history

## Error Messages

- "Invalid QR - Ticket not found"
- "QR already scanned - All entries used"
- "Attraction mismatch - Ticket not valid for [Attraction]"

## Future Enhancements

- API integration for real-time ticket fetching
- Background sync service for offline/online data
- Web dashboard for monitoring
- Multi-language support
- Sound notifications
- LED indicators for hardware integration

## Hardware Requirements

- Raspberry Pi (any model)
- USB Camera
- Display (HDMI/Touchscreen)
- Optional: LED indicators, buzzer, relay for gate control

## Production Deployment

For production use as turnstile/flap barrier controller:

1. Remove test tickets and sample data
2. Integrate with real ticket API
3. Add hardware control for gates
4. Implement proper logging and monitoring
5. Add security measures
6. Configure auto-start on boot
