#!/bin/bash
# SOU Raspberry Pi Setup Script
# Run this script on the Raspberry Pi after deployment

echo "🚀 SOU Raspberry Pi Setup Script"
echo "================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root"
    echo "Run as: bash setup_pi.sh"
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y python3-opencv python3-pip libzbar0

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt

# Add user to video group for camera access
echo "📹 Adding user to video group..."
sudo usermod -a -G video $USER

# Make scripts executable
echo "🔐 Setting script permissions..."
chmod +x *.py

# Create desktop shortcuts (optional)
echo "🖥️ Creating desktop shortcuts..."
cat > ~/Desktop/AttractionA.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Attraction A Scanner
Comment=SOU Attraction A QR Scanner
Exec=python3 /home/$USER/SOU/AttractionA.py
Icon=applications-multimedia
Terminal=true
Categories=AudioVideo;
EOF

cat > ~/Desktop/AttractionB.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Attraction B Scanner
Comment=SOU Attraction B QR Scanner
Exec=python3 /home/$USER/SOU/AttractionB.py
Icon=applications-multimedia
Terminal=true
Categories=AudioVideo;
EOF

cat > ~/Desktop/AttractionC.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Attraction C Scanner
Comment=SOU Attraction C QR Scanner
Exec=python3 /home/$USER/SOU/AttractionC.py
Icon=applications-multimedia
Terminal=true
Categories=AudioVideo;
EOF

# Make desktop files executable
chmod +x ~/Desktop/*.desktop

# Test camera
echo "📷 Testing camera..."
if [ -e /dev/video0 ]; then
    echo "✅ Camera device found: /dev/video0"
else
    echo "⚠️  Camera device not found. Please check USB camera connection."
fi

# Test display
echo "🖥️ Testing display..."
if [ -n "$DISPLAY" ]; then
    echo "✅ Display environment: $DISPLAY"
else
    echo "⚠️  No display environment found. Make sure you're in a desktop session."
fi

# Run test
echo "🧪 Running system test..."
python3 test_attractions.py

echo ""
echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Reboot to apply group changes: sudo reboot"
echo "2. After reboot, test camera: python3 camera_test.py"
echo "3. Run attraction scanner: python3 AttractionA.py"
echo ""
echo "🎯 Available applications:"
echo "   - AttractionA.py (Gate A)"
echo "   - AttractionB.py (Gate B)"
echo "   - AttractionC.py (Gate C)"
echo "   - test_attractions.py (Test without camera)"
echo ""
echo "📖 See ATTRACTION_README.md for detailed usage instructions"
