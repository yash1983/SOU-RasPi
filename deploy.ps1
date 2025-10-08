# SOU-RasPi Deployment Script
# This script helps deploy code to your Raspberry Pi

param(
    [string]$PiIP = "192.168.8.56",
    [string]$PiUser = "yashr",
    [string]$RemotePath = "/home/yashr/SOU",
    [string]$Method = "scp"
)

Write-Host "🚀 Deploying to Raspberry Pi at $PiIP" -ForegroundColor Green

# Test connection first
Write-Host "Testing connection to $PiIP..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $PiIP -Count 1 -Quiet
if (-not $ping) {
    Write-Host "❌ Cannot reach Raspberry Pi at $PiIP" -ForegroundColor Red
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "  - Pi is powered on and connected to WiFi" -ForegroundColor Yellow
    Write-Host "  - IP address is correct" -ForegroundColor Yellow
    Write-Host "  - Both devices are on the same network" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Connection successful!" -ForegroundColor Green

switch ($Method.ToLower()) {
    "rsync" {
        Write-Host "Using rsync method..." -ForegroundColor Cyan
        # Check if rsync is available
        try {
            $rsyncVersion = & rsync --version 2>$null
            if ($LASTEXITCODE -ne 0) {
                throw "rsync not found"
            }
        }
        catch {
            Write-Host "❌ rsync not found. Please install rsync or use SCP method." -ForegroundColor Red
            Write-Host "You can install rsync via WSL, Git Bash, or use the SCP method instead." -ForegroundColor Yellow
            exit 1
        }
        
        # Create remote directory if it doesn't exist
        Write-Host "Creating remote directory..." -ForegroundColor Yellow
        ssh -i $env:USERPROFILE\.ssh\keyfile $PiUser@$PiIP "sudo mkdir -p $RemotePath && sudo chown yash:yash $RemotePath"
        
        # Sync files using rsync
        Write-Host "Syncing files..." -ForegroundColor Yellow
        rsync -avz --delete --exclude='.git' --exclude='*.log' --exclude='node_modules' -e "ssh -i $env:USERPROFILE\.ssh\keyfile" ./ $PiUser@$PiIP`:$RemotePath/
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Deployment successful!" -ForegroundColor Green
        } else {
            Write-Host "❌ Deployment failed!" -ForegroundColor Red
        }
    }
    
    "scp" {
        Write-Host "Using SCP method..." -ForegroundColor Cyan
        
        # Create remote directory
        Write-Host "Creating remote directory..." -ForegroundColor Yellow
        ssh -i $env:USERPROFILE\.ssh\keyfile $PiUser@$PiIP "sudo mkdir -p $RemotePath && sudo chown yash:yash $RemotePath"
        
        # Copy files
        Write-Host "Copying files..." -ForegroundColor Yellow
        scp -i $env:USERPROFILE\.ssh\keyfile -r -o StrictHostKeyChecking=no ./* $PiUser@$PiIP`:$RemotePath/
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Deployment successful!" -ForegroundColor Green
        } else {
            Write-Host "❌ Deployment failed!" -ForegroundColor Red
        }
    }
    
    "git" {
        Write-Host "Using Git method..." -ForegroundColor Cyan
        Write-Host "This will pull the latest code from your Git repository on the Pi." -ForegroundColor Yellow
        
        # SSH into Pi and pull latest code
        ssh -i $env:USERPROFILE\.ssh\keyfile $PiUser@$PiIP "cd $RemotePath && git pull origin main"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Git pull successful!" -ForegroundColor Green
        } else {
            Write-Host "❌ Git pull failed!" -ForegroundColor Red
        }
    }
    
    default {
        Write-Host "❌ Unknown method: $Method" -ForegroundColor Red
        Write-Host "Available methods: rsync, scp, git" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`n🎉 Deployment complete!" -ForegroundColor Green
Write-Host "You can now SSH into your Pi: ssh $PiUser@$PiIP" -ForegroundColor Cyan
