"""
System wake/sleep and restart event detection and handling
"""

import platform
import threading
import time
from typing import Callable, Optional
from .logger import setup_logger

logger = setup_logger(__name__)


class SystemEventMonitor:
    """Monitor system wake, sleep, and restart events"""
    
    def __init__(self, on_wake_callback: Optional[Callable] = None, 
                 on_restart_callback: Optional[Callable] = None):
        self.on_wake_callback = on_wake_callback
        self.on_restart_callback = on_restart_callback
        self.monitor_thread = None
        self.is_running = False
        self.system = platform.system()
        self.last_check = time.time()
        self.sleep_threshold = 300  # 5 minutes considered as wake event
    
    def start(self):
        """Start monitoring system events"""
        if self.is_running:
            logger.warning("Monitor already running")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"System event monitor started on {self.system}")
    
    def stop(self):
        """Stop monitoring system events"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("System event monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        if self.system == 'Windows':
            self._monitor_windows()
        elif self.system == 'Darwin':
            self._monitor_macos()
        elif self.system == 'Linux':
            self._monitor_linux()
        else:
            logger.warning(f"Unsupported system for event monitoring: {self.system}")
    
    def _monitor_windows(self):
        """Monitor Windows sleep/wake events"""
        try:
            import win32api
            import win32con
            import win32event
            import win32evtlog
            
            logger.info("Windows event monitoring initialized")
            
            while self.is_running:
                try:
                    # Check for power state changes via registry
                    import winreg
                    
                    # Simple approach: check system uptime
                    current_time = time.time()
                    time_since_last_check = current_time - self.last_check
                    
                    if time_since_last_check > self.sleep_threshold:
                        logger.info(f"Detected wake event (gap: {time_since_last_check}s)")
                        if self.on_wake_callback:
                            self.on_wake_callback()
                    
                    self.last_check = current_time
                    time.sleep(30)  # Check every 30 seconds
                
                except Exception as e:
                    logger.error(f"Error in Windows monitoring: {e}")
                    time.sleep(60)
        
        except ImportError:
            logger.warning("pywin32 not installed, using fallback polling")
            self._monitor_generic()
    
    def _monitor_macos(self):
        """Monitor macOS sleep/wake events using IOKit"""
        try:
            from Cocoa import NSWorkspace, NSWorkspaceWillSleepNotification, NSWorkspaceDidWakeNotification
            from Foundation import NSNotificationCenter, NSNotification
            import objc
            
            logger.info("macOS event monitoring initialized")
            
            def on_wake(notification):
                logger.info("macOS wake event detected")
                if self.on_wake_callback:
                    self.on_wake_callback()
            
            def on_sleep(notification):
                logger.info("macOS sleep event detected")
            
            # Register for notifications
            notification_center = NSNotificationCenter.defaultCenter()
            
            # Create observer object
            observer = objc.PyObjCDelegate(
                None,
                [on_wake, on_sleep],
                None
            )
            
            notification_center.addObserver_selector_name_object_(
                observer,
                on_wake,
                NSWorkspaceDidWakeNotification,
                None
            )
            
            # Keep the monitor running
            while self.is_running:
                time.sleep(1)
        
        except ImportError:
            logger.warning("Cocoa framework not available, using fallback polling")
            self._monitor_generic()
        except Exception as e:
            logger.error(f"Error in macOS monitoring: {e}")
            self._monitor_generic()
    
    def _monitor_linux(self):
        """Monitor Linux sleep/wake events using logind or ACPId"""
        try:
            import dbus
            from dbus.mainloop.glib import DBusGMainLoop
            
            DBusGMainLoop(set_as_default=True)
            bus = dbus.SystemBus()
            
            # Monitor systemd-logind for sleep/wake events
            logind = bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1')
            logind.connect_to_signal('PrepareForSleep', self._on_prepare_sleep)
            
            logger.info("Linux systemd-logind monitoring initialized")
            
            # Keep the monitor running
            from gi.repository import GLib
            loop = GLib.MainLoop()
            loop.run()
        
        except ImportError:
            logger.warning("dbus not available, using fallback polling")
            self._monitor_generic()
        except Exception as e:
            logger.error(f"Error in Linux monitoring: {e}")
            self._monitor_generic()
    
    def _on_prepare_sleep(self, going_to_sleep):
        """Callback for systemd-logind sleep signal"""
        if not going_to_sleep:  # False means waking up
            logger.info("Linux wake event detected")
            if self.on_wake_callback:
                self.on_wake_callback()
    
    def _monitor_generic(self):
        """Generic fallback monitoring using time delta"""
        logger.info("Using generic polling-based monitoring")
        
        while self.is_running:
            try:
                current_time = time.time()
                time_since_last_check = current_time - self.last_check
                
                # If gap is large, system likely woke from sleep
                if time_since_last_check > self.sleep_threshold:
                    logger.info(f"Detected potential wake event (gap: {time_since_last_check}s)")
                    if self.on_wake_callback:
                        self.on_wake_callback()
                
                self.last_check = current_time
                time.sleep(30)  # Check every 30 seconds
            
            except Exception as e:
                logger.error(f"Error in generic monitoring: {e}")
                time.sleep(60)


class SystemStateTracker:
    """Track system boot and wake events"""
    
    def __init__(self):
        self.boot_time = self._get_boot_time()
        self.last_activity = time.time()
    
    @staticmethod
    def _get_boot_time() -> float:
        """Get system boot time"""
        try:
            if platform.system() == 'Windows':
                import psutil
                return psutil.boot_time()
            elif platform.system() == 'Darwin':
                import subprocess
                result = subprocess.run(['sysctl', '-n', 'kern.boottime'], 
                                      capture_output=True, text=True)
                # Parse format: { sec = 1234567890, usec = 123456 }
                import re
                match = re.search(r'sec = (\d+)', result.stdout)
                if match:
                    return float(match.group(1))
            else:
                import subprocess
                result = subprocess.run(['uptime', '-s'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    from datetime import datetime
                    boot_str = result.stdout.strip()
                    boot_dt = datetime.strptime(boot_str, '%Y-%m-%d %H:%M:%S')
                    return boot_dt.timestamp()
        except Exception as e:
            logger.error(f"Could not get boot time: {e}")
        
        return time.time()
    
    def is_system_restarted(self) -> bool:
        """Check if system has been restarted since last check"""
        current_boot = self._get_boot_time()
        if current_boot > self.boot_time:
            logger.info("System restart detected")
            self.boot_time = current_boot
            return True
        return False
    
    def has_been_sleeping(self) -> bool:
        """Check if system has been in sleep state"""
        current_time = time.time()
        gap = current_time - self.last_activity
        
        if gap > self.sleep_threshold:
            logger.info(f"Sleep detected (gap: {gap}s)")
            self.last_activity = current_time
            return True
        
        self.last_activity = current_time
        return False