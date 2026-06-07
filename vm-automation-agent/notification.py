"""
Desktop notification system
"""

import platform
import subprocess
from typing import Optional
from .logger import setup_logger

logger = setup_logger(__name__)


class NotificationManager:
    """Cross-platform desktop notification manager"""
    
    def __init__(self, config):
        self.config = config
        self.system = platform.system()
    
    def show_notification(self, title: str, message: str, duration: Optional[int] = None) -> bool:
        """
        Show desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            duration: Display duration in seconds (None = use config)
        
        Returns:
            True if notification shown successfully
        """
        if not self.config.notification.enable_popup:
            logger.debug("Notifications disabled in config")
            return False
        
        duration = duration or self.config.notification.show_duration
        
        try:
            if self.system == 'Windows':
                return self._notify_windows(title, message, duration)
            elif self.system == 'Darwin':
                return self._notify_macos(title, message, duration)
            elif self.system == 'Linux':
                return self._notify_linux(title, message, duration)
            else:
                logger.warning(f"Unsupported OS for notifications: {self.system}")
                return False
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
            return False
    
    def _notify_windows(self, title: str, message: str, duration: int) -> bool:
        """Show notification on Windows using PowerShell"""
        try:
            # PowerShell toast notification
            ps_script = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
$APP_ID = 'VMAuto Agent'
$template = @"
<toast>
    <visual>
        <binding template="ToastText02">
            <text id="1">{title}</text>
            <text id="2">{message}</text>
        </binding>
    </visual>
</toast>
"@
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
"""
            
            # Try PowerShell first
            try:
                subprocess.run([
                    'powershell', '-NoProfile', '-Command', ps_script
                ], timeout=5)
                logger.info(f"Windows notification shown: {title}")
                return True
            except Exception:
                # Fallback to msg command
                subprocess.run([
                    'msg', '*', f"/TIME:{duration} {title}: {message}"
                ], timeout=5)
                logger.info(f"Windows msg notification shown: {title}")
                return True
        
        except Exception as e:
            logger.error(f"Windows notification failed: {e}")
            return False
    
    def _notify_macos(self, title: str, message: str, duration: int) -> bool:
        """Show notification on macOS using osascript"""
        try:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run([
                'osascript', '-e', script
            ], timeout=5)
            logger.info(f"macOS notification shown: {title}")
            return True
        except Exception as e:
            logger.error(f"macOS notification failed: {e}")
            return False
    
    def _notify_linux(self, title: str, message: str, duration: int) -> bool:
        """Show notification on Linux using notify-send"""
        try:
            # Try dbus/systemd notification daemon
            subprocess.run([
                'notify-send',
                '-t', str(duration * 1000),
                title,
                message
            ], timeout=5)
            logger.info(f"Linux notification shown: {title}")
            return True
        except FileNotFoundError:
            logger.warning("notify-send not found on Linux system")
            return False
        except Exception as e:
            logger.error(f"Linux notification failed: {e}")
            return False
    
    def show_success_notification(self, message: str = None) -> bool:
        """Show success notification for completed data import"""
        if message is None:
            from datetime import datetime
            today = datetime.now().strftime("%B %d, %Y")
            message = f"Today's data ({today}) has been successfully imported!"
        
        return self.show_notification(
            title=self.config.notification.title,
            message=message,
            duration=self.config.notification.show_duration
        )
    
    def show_error_notification(self, error: str) -> bool:
        """Show error notification"""
        return self.show_notification(
            title=f"{self.config.notification.title} - Error",
            message=f"An error occurred: {error}",
            duration=self.config.notification.show_duration + 5
        )