#!/bin/bash
# SOU Raspberry Pi - Dependencies Installation Script (Optimized for 1GB RAM)

echo "🔧 Installing dependencies for SOU Raspberry Pi project (1GB RAM optimized)..."

# Check available memory
echo "💾 Checking system memory..."
free -h

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y python3-pip python3-venv libzbar0 libzbar-dev sqlite3

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install Python packages with memory optimization
echo "📦 Installing Python packages (memory optimized)..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

echo "✅ Dependencies installed successfully!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To test the camera, run:"
echo "  python3 camera_test.py"