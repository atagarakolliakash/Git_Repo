"""
Configuration management for VM Automation Agent
"""
 
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import json
 
 
@dataclass
class DatabaseConfig:
    """PostgreSQL database configuration"""
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "postgres"
    connection_timeout: int = 30
    max_retries: int = 5
    retry_delay: int = 5  # seconds
 
 
@dataclass
class VirtualBoxConfig:
    """VirtualBox configuration"""
    vbox_path: Optional[str] = None
    vm_name_pattern: str = "pg*"
    startup_timeout: int = 120  # seconds
    health_check_interval: int = 5  # seconds
    max_startup_attempts: int = 3
 
 
@dataclass
class NotificationConfig:
    """System notification configuration"""
    enable_popup: bool = True
    title: str = "VM Automation Agent"
    show_duration: int = 5  # seconds
 
 
@dataclass
class LogConfig:
    """Logging configuration"""
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    log_dir: Path = Path.home() / ".vm_agent" / "logs"
 
 
class Config:
    """Main configuration class"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or str(Path.home() / ".vm_agent" / "config.json")
        self.db = DatabaseConfig()
        self.vbox = VirtualBoxConfig()
        self.notification = NotificationConfig()
        self.log = LogConfig()
        
        # Ensure log directory exists
        self.log.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to load from config file
        if os.path.exists(self.config_file):
            self.load_from_file()
    
    def load_from_file(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            if 'database' in config_data:
                self.db = DatabaseConfig(**config_data['database'])
            if 'virtualbox' in config_data:
                self.vbox = VirtualBoxConfig(**config_data['virtualbox'])
            if 'notification' in config_data:
                self.notification = NotificationConfig(**config_data['notification'])
            if 'logging' in config_data:
                log_config = config_data['logging']
                if 'log_dir' in log_config:
                    log_config['log_dir'] = Path(log_config['log_dir'])
                self.log = LogConfig(**log_config)
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_file}: {e}")
    
    def save_to_file(self):
        """Save current configuration to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            config_data = {
                'database': {
                    'host': self.db.host,
                    'port': self.db.port,
                    'user': self.db.user,
                    'password': self.db.password,
                    'database': self.db.database,
                    'connection_timeout': self.db.connection_timeout,
                    'max_retries': self.db.max_retries,
                    'retry_delay': self.db.retry_delay,
                },
                'virtualbox': {
                    'vbox_path': self.vbox.vbox_path,
                    'vm_name_pattern': self.vbox.vm_name_pattern,
                    'startup_timeout': self.vbox.startup_timeout,
                    'health_check_interval': self.vbox.health_check_interval,
                    'max_startup_attempts': self.vbox.max_startup_attempts,
                },
                'notification': {
                    'enable_popup': self.notification.enable_popup,
                    'title': self.notification.title,
                    'show_duration': self.notification.show_duration,
                },
                'logging': {
                    'log_level': self.log.log_level,
                    'log_file': str(self.log.log_file) if self.log.log_file else None,
                    'log_dir': str(self.log.log_dir),
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            print(f"Warning: Could not save config to {self.config_file}: {e}")
 
