"""
Main VM Automation Agent - Orchestrates all components
"""

import time
from typing import List, Optional
from .config import Config
from .logger import setup_logger
from .virtualbox import VirtualBoxManager
from .database import DatabaseManager
from .notification import NotificationManager
from .system_events import SystemEventMonitor, SystemStateTracker

logger = setup_logger(__name__)


class VMAutomationAgent:
    """
    Main automation agent that orchestrates VM startup and database seeding
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the agent
        
        Args:
            config_file: Path to configuration JSON file
        """
        self.config = Config(config_file)
        logger.info(f"Config loaded from {self.config.config_file}")
        
        # Initialize components
        self.vbox_manager = VirtualBoxManager(self.config)
        self.db_manager = DatabaseManager(self.config)
        self.notification_manager = NotificationManager(self.config)
        self.system_tracker = SystemStateTracker()
        self.system_monitor = None
        
        self.is_running = False
        self.last_execution_time = None
    
    def _on_system_wake(self):
        """Callback when system wakes from sleep"""
        logger.info("=== System wake event detected ===")
        
        # Debounce: don't run if we just ran
        if self.last_execution_time:
            time_since_last_run = time.time() - self.last_execution_time
            if time_since_last_run < 60:  # 1 minute debounce
                logger.info(f"Ignoring wake event (ran {time_since_last_run}s ago)")
                return
        
        self.execute_automation()
    
    def _on_system_restart(self):
        """Callback when system restarts"""
        logger.info("=== System restart detected ===")
        
        # Small delay to allow services to start
        time.sleep(10)
        self.execute_automation()
    
    def execute_automation(self) -> bool:
        """
        Execute the main automation workflow:
        1. Start PostgreSQL VMs
        2. Wait for VMs to be running
        3. Connect to database
        4. Insert sample data
        5. Show success notification
        
        Returns:
            True if automation completed successfully
        """
        logger.info("=" * 60)
        logger.info("Starting VM Automation workflow")
        logger.info("=" * 60)
        
        try:
            # Step 1: Start VMs
            logger.info("Step 1: Starting PostgreSQL VMs...")
            started_vms = self.vbox_manager.startup_pg_vms()
            
            if not started_vms:
                error_msg = "No PostgreSQL VMs were started"
                logger.error(error_msg)
                self.notification_manager.show_error_notification(error_msg)
                return False
            
            logger.info(f"Started VMs: {started_vms}")
            
            # Step 2: Wait for VMs to be fully ready
            logger.info("Step 2: Waiting for VMs to be fully ready...")
            time.sleep(10)  # Additional wait for services to start
            
            # Step 3: Connect to database
            logger.info("Step 3: Connecting to database...")
            if not self.db_manager.connect():
                error_msg = "Failed to connect to PostgreSQL database"
                logger.error(error_msg)
                self.notification_manager.show_error_notification(error_msg)
                return False
            
            # Step 4: Insert sample data
            logger.info("Step 4: Inserting sample data...")
            num_records = self.config.db.max_retries if hasattr(self.config.db, 'max_retries') else 12
            
            if not self.db_manager.insert_sample_data(num_records=num_records):
                error_msg = "Failed to insert sample data"
                logger.error(error_msg)
                self.notification_manager.show_error_notification(error_msg)
                self.db_manager.disconnect()
                return False
            
            # Verify data
            logger.info("Step 5: Verifying inserted data...")
            data_summary = self.db_manager.verify_data_inserted()
            
            if data_summary:
                logger.info("Data verification summary:")
                for table, count in data_summary.items():
                    logger.info(f"  - {table}: {count} records")
            
            # Disconnect
            self.db_manager.disconnect()
            
            # Step 6: Show success notification
            logger.info("Step 6: Showing success notification...")
            self.notification_manager.show_success_notification()
            
            logger.info("=" * 60)
            logger.info("VM Automation workflow completed successfully!")
            logger.info("=" * 60)
            
            self.last_execution_time = time.time()
            return True
        
        except Exception as e:
            logger.error(f"Unexpected error during automation: {e}", exc_info=True)
            self.notification_manager.show_error_notification(str(e))
            return False
    
    def start(self):
        """Start the automation agent with system event monitoring"""
        if self.is_running:
            logger.warning("Agent already running")
            return
        
        self.is_running = True
        logger.info("Starting VM Automation Agent")
        
        # Initialize system event monitor
        self.system_monitor = SystemEventMonitor(
            on_wake_callback=self._on_system_wake,
            on_restart_callback=self._on_system_restart
        )
        self.system_monitor.start()
        
        # Run initial automation on startup
        logger.info("Running initial automation on agent start...")
        self.execute_automation()
        
        logger.info("Agent started and listening for system events")
    
    def stop(self):
        """Stop the automation agent"""
        if not self.is_running:
            logger.warning("Agent not running")
            return
        
        logger.info("Stopping VM Automation Agent")
        
        if self.system_monitor:
            self.system_monitor.stop()
        
        if self.db_manager.connection:
            self.db_manager.disconnect()
        
        self.is_running = False
        logger.info("Agent stopped")
    
    def run_once(self) -> bool:
        """Run automation once and exit (for testing)"""
        logger.info("Running automation once...")
        return self.execute_automation()
    
    def configure(self, **kwargs) -> bool:
        """
        Update configuration and save
        
        Example:
            agent.configure(
                db_host='192.168.1.100',
                db_port=5432,
                db_user='admin'
            )
        
        Returns:
            True if configuration updated successfully
        """
        try:
            # Map kwargs to config objects
            for key, value in kwargs.items():
                if key.startswith('db_'):
                    attr = key.replace('db_', '')
                    setattr(self.config.db, attr, value)
                elif key.startswith('vbox_'):
                    attr = key.replace('vbox_', '')
                    setattr(self.config.vbox, attr, value)
                elif key.startswith('notify_'):
                    attr = key.replace('notify_', '')
                    setattr(self.config.notification, attr, value)
            
            self.config.save_to_file()
            logger.info(f"Configuration updated: {kwargs}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_status(self) -> dict:
        """Get current agent status"""
        return {
            'running': self.is_running,
            'last_execution': self.last_execution_time,
            'vbox_path': self.vbox_manager.vbox_path if self.vbox_manager.vbox_path else 'Not found',
            'pg_vms': self.vbox_manager.find_pg_vms(),
            'config_file': self.config.config_file,
        }