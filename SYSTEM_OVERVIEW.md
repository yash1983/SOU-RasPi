# SOU Raspberry Pi System - Updated Architecture

## Overview

The SOU Raspberry Pi system has been updated to support a new database structure and background services for server synchronization. The system now supports separate tracking for each attraction with individual person counts and usage tracking.

## New Features

### 1. Updated Database Structure

The database now supports separate columns for each attraction:
- `A_pax`, `A_used` - Attraction A allowed and used persons
- `B_pax`, `B_used` - Attraction B allowed and used persons  
- `C_pax`, `C_used` - Attraction C allowed and used persons
- `booking_date` - Date of booking
- `reference_no` - Reference number (same as ticket_no)

### 2. Background Services

#### Fetch Service (`fetch_service.py`)
- Fetches tickets from server API
- Creates/updates local database records
- Runs every 5 minutes (configurable)
- Handles network errors gracefully

#### Sync Service (`sync_service.py`)
- Syncs unsynced records back to server
- Runs continuously with 1-second intervals
- Pushes one record at a time via HTTP POST
- Marks records as synced after successful upload

### 3. Configuration System (`config.py`)
- Centralized configuration management
- API endpoints configurable
- Service intervals configurable
- Logging settings configurable

## File Structure

```
├── config.py                 # Configuration management
├── ticket_database.py        # Updated database manager
├── fetch_service.py          # Background fetch service
├── sync_service.py           # Background sync service
├── service_manager.py        # Service management
├── start_services.py         # Service startup script
├── migrate_database.py       # Database migration script
├── AttractionA.py           # Attraction A scanner (updated)
├── AttractionB.py           # Attraction B scanner (updated)
├── AttractionC.py           # Attraction C scanner (updated)
├── display_manager.py       # Display management
└── config.json              # Configuration file (auto-generated)
```

## API Integration

### Server Data Format (GET)
```json
[{
  "bookingDate": "2025-10-09",
  "referenceNo": "20251009-000001",
  "attractions": {
    "A": {"pax": 1, "used": 0},
    "B": {"pax": 2, "used": 0},
    "C": {"pax": 3, "used": 0}
  }
}]
```

### Sync Data Format (POST)
```json
{
  "bookingDate": "2025-10-09",
  "referenceNo": "20251009-000001",
  "attractions": {
    "A": {"pax": 1, "used": 1},
    "B": {"pax": 2, "used": 0},
    "C": {"pax": 3, "used": 0}
  }
}
```

## Configuration

The system uses `config.json` for configuration:

```json
{
  "api": {
    "base_url": "http://demotms.aditonline.com/api/",
    "fetch_endpoint": "bookings/summary",
    "sync_endpoint": "bookings/update-used",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 5
  },
  "services": {
    "fetch_interval": 300,
    "sync_interval": 1,
    "fetch_enabled": true,
    "sync_enabled": true
  },
  "logging": {
    "level": "INFO",
    "file": "sou_system.log",
    "max_size": 10485760,
    "backup_count": 5
  }
}
```

## Usage

### 1. Migration (First Time Setup)

If you have existing databases, run the migration script:

```bash
python3 migrate_database.py
```

This will:
- Create backups of existing databases
- Convert old structure to new structure
- Preserve all existing data

### 2. Start Background Services

```bash
python3 start_services.py
```

This starts both fetch and sync services in the background.

### 3. Run Attraction Scanners

```bash
# Terminal 1 - Attraction A
python3 AttractionA.py

# Terminal 2 - Attraction B  
python3 AttractionB.py

# Terminal 3 - Attraction C
python3 AttractionC.py
```

### 4. Individual Service Management

```bash
# Start only fetch service
python3 fetch_service.py

# Start only sync service
python3 sync_service.py
```

## Ticket Format

**Live tickets** use the format: `20251009-000001`, `20251009-000002`, etc.

**Dummy/test tickets** use the format: `20251009-000001-dummy`, `20251009-000002-dummy`, etc.

## Key Changes

1. **Database Schema**: Separate columns for each attraction
2. **Validation Logic**: Checks specific attraction columns
3. **Sync Behavior**: `is_synced` flag resets to 0 when persons are allowed
4. **Background Services**: Automated fetch and sync
5. **Configuration**: Centralized settings management
6. **Error Handling**: Robust network error handling
7. **Logging**: Comprehensive logging system

## Monitoring

- Check `sou_system.log` for service logs
- Use `python3 -c "from ticket_database import TicketDatabase; print(TicketDatabase('AttractionA').get_stats())"` for stats
- Services automatically restart if they fail

## Production Deployment

1. Update `config.json` with production API endpoints
2. Run migration script if needed
3. Start services: `python3 start_services.py`
4. Start attraction scanners
5. Monitor logs for any issues

## Troubleshooting

- **Services not starting**: Check `config.json` and API connectivity
- **Database errors**: Run migration script
- **Sync issues**: Check network connectivity and API endpoints
- **Performance issues**: Adjust intervals in configuration
