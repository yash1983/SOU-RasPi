# Manual Deployment Instructions

## SSH Key Setup (Required)

Since the Raspberry Pi requires SSH key authentication, you need to set up SSH keys first:

### 1. Generate SSH Key (if you don't have one)
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

### 2. Copy Public Key to Raspberry Pi
```bash
ssh-copy-id yashr@192.168.8.56
```

### 3. Test SSH Connection
```bash
ssh yashr@192.168.8.56
```

## Manual Deployment Steps

### Option 1: Using SCP (after SSH key setup)
```bash
# Create directory on Pi
ssh yashr@192.168.8.56 "mkdir -p /home/yashr/SOU-RasPi"

# Copy all files
scp -r ./* yashr@192.168.8.56:/home/yashr/SOU-RasPi/
```

### Option 2: Using Git (if repository is set up)
```bash
# SSH into Pi
ssh yashr@192.168.8.56

# Clone or pull repository
cd /home/yashr
git clone <your-repo-url> SOU-RasPi
# OR if already cloned:
cd SOU-RasPi && git pull origin main
```

### Option 3: Using USB/SD Card
1. Copy all files to a USB drive or SD card
2. Insert into Raspberry Pi
3. Copy files to `/home/yashr/SOU-RasPi/`

## Post-Deployment Setup

After deploying the files, SSH into the Pi and run:

```bash
# SSH into Pi
ssh yashr@192.168.8.56

# Navigate to project directory
cd /home/yashr/SOU-RasPi

# Install Python dependencies
pip3 install -r requirements.txt

# Install system dependencies
sudo apt-get update
sudo apt-get install python3-opencv libzbar0

# Make scripts executable
chmod +x *.py

# Test the system
python3 test_attractions.py
```

## Running the Attraction Scanners

```bash
# For Attraction A
python3 AttractionA.py

# For Attraction B  
python3 AttractionB.py

# For Attraction C
python3 AttractionC.py
```

## Files to Deploy

Make sure these files are copied to the Raspberry Pi:

### Core Application Files:
- `AttractionA.py`
- `AttractionB.py` 
- `AttractionC.py`
- `ticket_database.py`
- `display_manager.py`
- `test_attractions.py`

### Configuration Files:
- `requirements.txt`
- `ATTRACTION_README.md`

### Deployment Scripts (optional):
- `deploy.sh`
- `deploy.ps1`

## Troubleshooting

### SSH Connection Issues:
1. Check if SSH is enabled on Pi: `sudo systemctl status ssh`
2. Check Pi's IP address: `hostname -I`
3. Ensure both devices are on same network

### Permission Issues:
```bash
# Fix file permissions
chmod +x *.py
chmod 644 *.txt *.md
```

### Camera Issues:
```bash
# Add user to video group
sudo usermod -a -G video yashr

# Check camera
lsusb | grep -i camera
```

### Display Issues:
```bash
# Check display
echo $DISPLAY
xrandr
```
