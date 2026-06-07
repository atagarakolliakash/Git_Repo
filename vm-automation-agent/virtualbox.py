"""
VirtualBox VM management and control
"""

import subprocess
import time
import platform
from typing import List, Optional
from pathlib import Path
from .logger import setup_logger

logger = setup_logger(__name__)


class VirtualBoxManager:
    """Manage VirtualBox virtual machines"""
    
    def __init__(self, config):
        self.config = config
        self.vbox_path = self._find_vboxmanage()
    
    def _find_vboxmanage(self) -> str:
        """Find VBoxManage executable path"""
        if self.config.vbox.vbox_path:
            return self.config.vbox.vbox_path
        
        system = platform.system()
        
        # Try common paths
        common_paths = {
            'Windows': [
                r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
                r"C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe",
            ],
            'Darwin': [
                "/usr/local/bin/VBoxManage",
                "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage",
            ],
            'Linux': [
                "/usr/bin/VBoxManage",
                "/usr/local/bin/VBoxManage",
            ]
        }
        
        for path_str in common_paths.get(system, []):
            if Path(path_str).exists():
                logger.info(f"Found VBoxManage at: {path_str}")
                return path_str
        
        # Try 'which' on Unix-like systems
        if system != 'Windows':
            try:
                result = subprocess.run(['which', 'VBoxManage'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    path = result.stdout.strip()
                    logger.info(f"Found VBoxManage via which: {path}")
                    return path
            except Exception:
                pass
        
        logger.error("VBoxManage not found. Please install VirtualBox.")
        raise FileNotFoundError("VBoxManage executable not found")
    
    def _run_command(self, *args) -> tuple[int, str, str]:
        """
        Run a VBoxManage command
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd = [self.vbox_path] + list(args)
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {' '.join(cmd)}")
            return -1, "", "Command timeout"
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return -1, "", str(e)
    
    def list_vms(self) -> List[str]:
        """Get list of all VMs"""
        returncode, stdout, stderr = self._run_command('list', 'vms')
        
        if returncode != 0:
            logger.error(f"Failed to list VMs: {stderr}")
            return []
        
        vms = []
        for line in stdout.strip().split('\n'):
            if line.strip():
                vm_name = line.split('"')[1]
                vms.append(vm_name)
        
        logger.info(f"Found VMs: {vms}")
        return vms
    
    def find_pg_vms(self) -> List[str]:
        """Find VMs matching PostgreSQL pattern (names starting with 'pg')"""
        all_vms = self.list_vms()
        pg_vms = [vm for vm in all_vms if vm.lower().startswith('pg')]
        
        if not pg_vms:
            logger.warning("No VMs matching pattern 'pg*' found")
        else:
            logger.info(f"Found PostgreSQL VMs: {pg_vms}")
        
        return pg_vms
    
    def get_vm_state(self, vm_name: str) -> str:
        """
        Get current state of a VM
        
        Returns: 'running', 'paused', 'saved', 'poweroff', 'unknown'
        """
        returncode, stdout, stderr = self._run_command('showvminfo', vm_name, '--machinereadable')
        
        if returncode != 0:
            logger.error(f"Failed to get state of {vm_name}: {stderr}")
            return 'unknown'
        
        for line in stdout.split('\n'):
            if line.startswith('VMState='):
                state = line.split('=')[1].strip('"')
                # Map VirtualBox states to simple names
                state_map = {
                    'running': 'running',
                    'paused': 'paused',
                    'saved': 'saved',
                    'poweroff': 'poweroff',
                }
                return state_map.get(state, state)
        
        return 'unknown'
    
    def start_vm(self, vm_name: str, headless: bool = True) -> bool:
        """
        Start a VM
        
        Args:
            vm_name: Name of the VM
            headless: If True, start without GUI
        
        Returns:
            True if successful, False otherwise
        """
        mode = 'headless' if headless else 'gui'
        logger.info(f"Starting VM '{vm_name}' in {mode} mode...")
        
        returncode, stdout, stderr = self._run_command('startvm', vm_name, '--type', mode)
        
        if returncode != 0:
            logger.error(f"Failed to start VM '{vm_name}': {stderr}")
            return False
        
        logger.info(f"VM '{vm_name}' start command sent")
        return True
    
    def wait_for_vm(self, vm_name: str, timeout: int = None) -> bool:
        """
        Wait for a VM to reach running state
        
        Args:
            vm_name: Name of the VM
            timeout: Maximum seconds to wait (None = use config)
        
        Returns:
            True if VM is running, False if timeout
        """
        timeout = timeout or self.config.vbox.startup_timeout
        interval = self.config.vbox.health_check_interval
        elapsed = 0
        
        logger.info(f"Waiting for VM '{vm_name}' to start (timeout: {timeout}s)...")
        
        while elapsed < timeout:
            state = self.get_vm_state(vm_name)
            logger.debug(f"VM '{vm_name}' state: {state}")
            
            if state == 'running':
                logger.info(f"VM '{vm_name}' is now running")
                return True
            
            time.sleep(interval)
            elapsed += interval
        
        logger.error(f"Timeout waiting for VM '{vm_name}' to start")
        return False
    
    def startup_pg_vms(self) -> List[str]:
        """
        Find and start all PostgreSQL VMs
        
        Returns:
            List of successfully started VM names
        """
        pg_vms = self.find_pg_vms()
        
        if not pg_vms:
            logger.warning("No PostgreSQL VMs found to start")
            return []
        
        started_vms = []
        
        for vm_name in pg_vms:
            state = self.get_vm_state(vm_name)
            
            if state == 'running':
                logger.info(f"VM '{vm_name}' is already running")
                started_vms.append(vm_name)
                continue
            
            # Try to start the VM
            if self.start_vm(vm_name):
                if self.wait_for_vm(vm_name):
                    started_vms.append(vm_name)
                    # Small delay between VM startups
                    time.sleep(3)
            
            time.sleep(1)
        
        return started_vms