"""Task scheduling and automation."""

import os
import logging
from datetime import datetime, time
from typing import Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

logger = logging.getLogger(__name__)


class PostingScheduler:
    """Manages scheduled posting tasks."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.posting_time = os.getenv("POSTING_TIME", "09:00")
        self.timezone = pytz.timezone(os.getenv("POSTING_TIMEZONE", "UTC"))
        self.max_posts_per_day = int(os.getenv("MAX_POSTS_PER_DAY", 1))
        self.is_running = False
    
    def start(self):
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
    
    def schedule_daily_posting(self, callback: Callable, job_id: str = "daily_post"):
        """Schedule daily posting at specified time.
        
        Args:
            callback: Function to call for posting
            job_id: Unique job identifier
        """
        try:
            hour, minute = map(int, self.posting_time.split(":"))
            
            # Remove existing job if it exists
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            self.scheduler.add_job(
                callback,
                CronTrigger(hour=hour, minute=minute, timezone=self.timezone),
                id=job_id,
                name="Daily LinkedIn Posting",
                replace_existing=True
            )
            
            logger.info(f"Scheduled daily posting at {self.posting_time} {self.timezone}")
            
        except Exception as e:
            logger.error(f"Error scheduling daily posting: {str(e)}")
    
    def schedule_profile_analysis(self, callback: Callable, interval_hours: int = 24):
        """Schedule periodic profile analysis.
        
        Args:
            callback: Function to call for analysis
            interval_hours: Interval in hours
        """
        try:
            job_id = "profile_analysis"
            
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            self.scheduler.add_job(
                callback,
                "interval",
                hours=interval_hours,
                id=job_id,
                name="Profile Analysis",
                replace_existing=True
            )
            
            logger.info(f"Scheduled profile analysis every {interval_hours} hours")
            
        except Exception as e:
            logger.error(f"Error scheduling profile analysis: {str(e)}")
    
    def schedule_engagement_tracking(self, callback: Callable, interval_hours: int = 6):
        """Schedule engagement metric updates.
        
        Args:
            callback: Function to call for tracking
            interval_hours: Interval in hours
        """
        try:
            job_id = "engagement_tracking"
            
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            self.scheduler.add_job(
                callback,
                "interval",
                hours=interval_hours,
                id=job_id,
                name="Engagement Tracking",
                replace_existing=True
            )
            
            logger.info(f"Scheduled engagement tracking every {interval_hours} hours")
            
        except Exception as e:
            logger.error(f"Error scheduling engagement tracking: {str(e)}")
    
    def schedule_content_generation(self, callback: Callable, interval_hours: int = 12):
        """Schedule content generation.
        
        Args:
            callback: Function to call for generation
            interval_hours: Interval in hours
        """
        try:
            job_id = "content_generation"
            
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            self.scheduler.add_job(
                callback,
                "interval",
                hours=interval_hours,
                id=job_id,
                name="Content Generation",
                replace_existing=True
            )
            
            logger.info(f"Scheduled content generation every {interval_hours} hours")
            
        except Exception as e:
            logger.error(f"Error scheduling content generation: {str(e)}")
    
    def get_jobs(self) -> list:
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()
    
    def get_job(self, job_id: str) -> Optional[dict]:
        """Get specific job details."""
        job = self.scheduler.get_job(job_id)
        if job:
            return {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time
            }
        return None
    
    def pause_job(self, job_id: str):
        """Pause a scheduled job."""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Job {job_id} paused")
        except Exception as e:
            logger.error(f"Error pausing job: {str(e)}")
    
    def resume_job(self, job_id: str):
        """Resume a paused job."""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Job {job_id} resumed")
        except Exception as e:
            logger.error(f"Error resuming job: {str(e)}")
    
    def remove_job(self, job_id: str):
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job {job_id} removed")
        except Exception as e:
            logger.error(f"Error removing job: {str(e)}")
