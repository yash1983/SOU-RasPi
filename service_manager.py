#!/usr/bin/env python3
"""
Service Manager for SOU Raspberry Pi
Manages background services (fetch and sync)
"""

import multiprocessing
import signal
import sys
import time
import logging
from config import config
from fetch_service import FetchService
from sync_service import SyncService
from cleanup_service import CleanupService

class ServiceManager:
    """Manages background services for SOU system"""
    
    def __init__(self):
        """Initialize service manager"""
        self.setup_logging()
        self.services = {}
        self.processes = {}
        self.running = False
        
        self.logger.info("Service Manager initialized")
    
    def setup_logging(self):
        """Setup logging for the service manager"""
        logging.basicConfig(
            level=getattr(logging, config.get('logging.level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.get('logging.file', 'sou_system.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ServiceManager')
    
    def start_fetch_service(self):
        """Start the fetch service in a separate process"""
        if config.get('services.fetch_enabled', True):
            self.logger.info("Starting Fetch Service...")
            process = multiprocessing.Process(target=self._run_fetch_service)
            process.start()
            self.processes['fetch'] = process
            self.logger.info("Fetch Service started")
        else:
            self.logger.info("Fetch Service is disabled")
    
    def start_sync_service(self):
        """Start the sync service in a separate process"""
        if config.get('services.sync_enabled', True):
            self.logger.info("Starting Sync Service...")
            process = multiprocessing.Process(target=self._run_sync_service)
            process.start()
            self.processes['sync'] = process
            self.logger.info("Sync Service started")
        else:
            self.logger.info("Sync Service is disabled")
    
    def start_cleanup_service(self):
        """Start the cleanup service in a separate process"""
        if config.get('services.cleanup_enabled', True):
            self.logger.info("Starting Cleanup Service...")
            process = multiprocessing.Process(target=self._run_cleanup_service)
            process.start()
            self.processes['cleanup'] = process
            self.logger.info("Cleanup Service started")
        else:
            self.logger.info("Cleanup Service is disabled")
    
    def _run_fetch_service(self):
        """Run fetch service in separate process"""
        try:
            service = FetchService()
            service.run()
        except Exception as e:
            self.logger.error(f"Fetch Service error: {e}")
    
    def _run_sync_service(self):
        """Run sync service in separate process"""
        try:
            service = SyncService()
            service.run()
        except Exception as e:
            self.logger.error(f"Sync Service error: {e}")
    
    def _run_cleanup_service(self):
        """Run cleanup service in separate process"""
        try:
            service = CleanupService()
            service.run()
        except Exception as e:
            self.logger.error(f"Cleanup Service error: {e}")
    
    def start_all_services(self):
        """Start all enabled services"""
        self.logger.info("Starting all services...")
        self.running = True
        
        # Start services
        self.start_fetch_service()
        self.start_sync_service()
        self.start_cleanup_service()
        
        self.logger.info("All services started")
    
    def stop_all_services(self):
        """Stop all running services"""
        self.logger.info("Stopping all services...")
        self.running = False
        
        for name, process in self.processes.items():
            if process.is_alive():
                self.logger.info(f"Stopping {name} service...")
                process.terminate()
                process.join(timeout=10)
                
                if process.is_alive():
                    self.logger.warning(f"Force killing {name} service...")
                    process.kill()
                    process.join()
                
                self.logger.info(f"{name} service stopped")
        
        self.processes.clear()
        self.logger.info("All services stopped")
    
    def check_services_health(self):
        """Check if all services are running properly"""
        healthy_services = 0
        total_services = len(self.processes)
        
        for name, process in self.processes.items():
            if process.is_alive():
                healthy_services += 1
                self.logger.debug(f"{name} service is healthy")
            else:
                self.logger.warning(f"{name} service is not running")
        
        if healthy_services == total_services and total_services > 0:
            self.logger.info(f"All {total_services} services are healthy")
            return True
        else:
            self.logger.warning(f"Only {healthy_services}/{total_services} services are healthy")
            return False
    
    def restart_service(self, service_name):
        """Restart a specific service"""
        if service_name in self.processes:
            self.logger.info(f"Restarting {service_name} service...")
            
            # Stop the service
            process = self.processes[service_name]
            if process.is_alive():
                process.terminate()
                process.join(timeout=10)
                if process.is_alive():
                    process.kill()
                    process.join()
            
            # Start the service again
            if service_name == 'fetch':
                self.start_fetch_service()
            elif service_name == 'sync':
                self.start_sync_service()
            elif service_name == 'cleanup':
                self.start_cleanup_service()
            
            self.logger.info(f"{service_name} service restarted")
        else:
            self.logger.error(f"Service {service_name} not found")
    
    def run(self):
        """Main service manager loop"""
        self.logger.info("Service Manager started")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Start all services
            self.start_all_services()
            
            # Monitor services
            while self.running:
                time.sleep(30)  # Check every 30 seconds
                
                if not self.check_services_health():
                    self.logger.warning("Some services are unhealthy, attempting restart...")
                    # Restart unhealthy services
                    for name, process in self.processes.items():
                        if not process.is_alive():
                            self.restart_service(name)
        
        except KeyboardInterrupt:
            self.logger.info("Service Manager interrupted by user")
        
        except Exception as e:
            self.logger.error(f"Unexpected error in Service Manager: {e}")
        
        finally:
            self.stop_all_services()
            self.logger.info("Service Manager stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

def main():
    """Main entry point for service manager"""
    manager = ServiceManager()
    manager.run()

if __name__ == "__main__":
    main()
