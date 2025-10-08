#!/bin/bash
# SOU-RasPi Deployment Script (Bash version)
# This script helps deploy code to your Raspberry Pi

PI_IP="192.168.8.56"
PI_USER="yashr"
REMOTE_PATH="/home/yashr/SOU"
METHOD="rsync"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --ip)
            PI_IP="$2"
            shift 2
            ;;
        --user)
            PI_USER="$2"
            shift 2
            ;;
        --path)
            REMOTE_PATH="$2"
            shift 2
            ;;
        --method)
            METHOD="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --ip IP        Raspberry Pi IP address (default: $PI_IP)"
            echo "  --user USER    SSH username (default: $PI_USER)"
            echo "  --path PATH    Remote path on Pi (default: $REMOTE_PATH)"
            echo "  --method METHOD Deployment method: rsync, scp, git (default: $METHOD)"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "🚀 Deploying to Raspberry Pi at $PI_IP"

# Test connection first
echo "Testing connection to $PI_IP..."
if ! ping -c 1 "$PI_IP" > /dev/null 2>&1; then
    echo "❌ Cannot reach Raspberry Pi at $PI_IP"
    echo "Please check:"
    echo "  - Pi is powered on and connected to WiFi"
    echo "  - IP address is correct"
    echo "  - Both devices are on the same network"
    exit 1
fi

echo "✅ Connection successful!"

case $METHOD in
    "rsync")
        echo "Using rsync method..."
        
        # Check if rsync is available
        if ! command -v rsync &> /dev/null; then
            echo "❌ rsync not found. Please install rsync or use SCP method."
            exit 1
        fi
        
        # Create remote directory if it doesn't exist
        echo "Creating remote directory..."
        ssh -i ~/.ssh/keyfile "$PI_USER@$PI_IP" "sudo mkdir -p $REMOTE_PATH && sudo chown yash:yash $REMOTE_PATH"
        
        # Sync files using rsync
        echo "Syncing files..."
        rsync -avz --delete --exclude='.git' --exclude='*.log' --exclude='node_modules' -e "ssh -i ~/.ssh/keyfile" ./ "$PI_USER@$PI_IP:$REMOTE_PATH/"
        
        if [ $? -eq 0 ]; then
            echo "✅ Deployment successful!"
        else
            echo "❌ Deployment failed!"
            exit 1
        fi
        ;;
        
    "scp")
        echo "Using SCP method..."
        
        # Create remote directory
        echo "Creating remote directory..."
        ssh -i ~/.ssh/keyfile "$PI_USER@$PI_IP" "sudo mkdir -p $REMOTE_PATH && sudo chown yash:yash $REMOTE_PATH"
        
        # Copy files
        echo "Copying files..."
        scp -i ~/.ssh/keyfile -r -o StrictHostKeyChecking=no ./* "$PI_USER@$PI_IP:$REMOTE_PATH/"
        
        if [ $? -eq 0 ]; then
            echo "✅ Deployment successful!"
        else
            echo "❌ Deployment failed!"
            exit 1
        fi
        ;;
        
    "git")
        echo "Using Git method..."
        echo "This will pull the latest code from your Git repository on the Pi."
        
        # SSH into Pi and pull latest code
        ssh -i ~/.ssh/keyfile "$PI_USER@$PI_IP" "cd $REMOTE_PATH && git pull origin main"
        
        if [ $? -eq 0 ]; then
            echo "✅ Git pull successful!"
        else
            echo "❌ Git pull failed!"
            exit 1
        fi
        ;;
        
    *)
        echo "❌ Unknown method: $METHOD"
        echo "Available methods: rsync, scp, git"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment complete!"
echo "You can now SSH into your Pi: ssh $PI_USER@$PI_IP"
