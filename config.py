#!/usr/bin/env python3
"""
Configuration Manager for SOU Raspberry Pi
Handles all configuration settings for the system
"""

import os
import json
from typing import Dict, Any

class Config:
    """Configuration manager for SOU system"""
    
    def __init__(self, config_file="config.json"):
        """Initialize configuration"""
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading config file: {e}")
                print("Using default configuration")
        
        # Default configuration
        default_config = {
            "api": {
                "base_url": "http://demotms.aditonline.com/api/",
                "fetch_endpoint": "bookings/summary",
                "sync_endpoint": "bookings/update-used",
                "timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 5
            },
            "services": {
                "fetch_interval": 300,  # 5 minutes
                "sync_interval": 1,     # 1 second
                "fetch_enabled": True,
                "sync_enabled": True,
                "skip_dummy_sync": True  # Skip syncing dummy tickets
            },
            "database": {
                "backup_enabled": True,
                "backup_interval": 3600,  # 1 hour
                "max_backups": 7
            },
            "logging": {
                "level": "INFO",
                "file": "sou_system.log",
                "max_size": 10485760,  # 10MB
                "backup_count": 5
            }
        }
        
        # Save default config
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving config file: {e}")
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'api.base_url')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        self.save_config()
    
    def get_api_url(self, endpoint: str = None) -> str:
        """Get full API URL for an endpoint"""
        base_url = self.get('api.base_url', 'http://somewhere.com/SOU/')
        if not base_url.endswith('/'):
            base_url += '/'
        
        if endpoint:
            return base_url + endpoint
        return base_url
    
    def get_fetch_url(self) -> str:
        """Get URL for fetching tickets"""
        endpoint = self.get('api.fetch_endpoint', 'tickets')
        return self.get_api_url(endpoint)
    
    def get_sync_url(self) -> str:
        """Get URL for syncing tickets"""
        endpoint = self.get('api.sync_endpoint', 'sync')
        return self.get_api_url(endpoint)

# Global config instance
config = Config()
