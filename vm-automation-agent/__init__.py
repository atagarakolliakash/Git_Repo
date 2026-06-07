
"""
VM Automation Agent Package
Auto-starts PostgreSQL VMs and seeds database with test data
"""
 
__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Automated VM startup and database seeding agent"
 
from .agent import VMAutomationAgent
from .config import Config
from .logger import setup_logger
 
__all__ = ["VMAutomationAgent", "Config", "setup_logger"]
 