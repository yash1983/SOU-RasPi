# SOU-RasPi

Raspberry Pi project for SOU (Southern Oregon University) - QR Code Scanner with USB Camera.

## Features

- USB Camera connection testing
- Real-time QR code scanning
- SQLite database with 1000 record limit (optimized for 1GB RAM)
- Automatic record cleanup
- Memory monitoring
- Easy deployment to Raspberry Pi
- Step-by-step testing framework

## Project Structure

```
SOU-RasPi/
├── camera_test.py              # Test USB camera connection
├── qr_scanner.py               # Basic QR code scanner
├── qr_scanner_optimized.py     # Memory-optimized QR scanner with database
├── database_manager.py         # SQLite database management
├── db_manager.py              # Interactive database manager
├── memory_monitor.py          # Memory usage monitoring
├── run_tests.py               # Interactive test runner
├── requirements.txt           # Python dependencies
├── install_dependencies.sh    # Installation script for Pi
├── deploy.ps1                # Windows deployment script
├── deploy.sh                 # Linux/Mac deployment script
└── README.md                 # This file
```

## Quick Start

### 1. Deploy to Raspberry Pi
```powershell
.\deploy.ps1 -Method scp
```

### 2. Install Dependencies on Pi
```bash
cd /opt/SOU
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### 3. Test Camera Connection
```bash
cd /opt/SOU
source venv/bin/activate
python3 camera_test.py
```

### 4. Run Optimized QR Scanner
```bash
python3 qr_scanner_optimized.py
```

### 5. Manage Database
```bash
python3 db_manager.py
```

### 6. Monitor Memory
```bash
python3 memory_monitor.py
```

## Usage

### Camera Test
Tests if your USB camera is working:
- Checks camera connection
- Shows camera properties
- Displays live preview
- Tests frame capture

### QR Scanner
Real-time QR code scanning:
- Continuous scanning
- Displays detected QR codes
- Saves frames with 's' key
- Quit with 'q' key

### Interactive Test Runner
```bash
python3 run_tests.py
```
Provides a menu to run different tests step by step.

## Requirements

- Raspberry Pi with USB camera
- Python 3.7+
- OpenCV
- pyzbar (QR code detection)

## Troubleshooting

- **Camera not found**: Check USB connection, try different camera indices
- **Permission denied**: Ensure user has camera access
- **Import errors**: Run `install_dependencies.sh` to install requirements
