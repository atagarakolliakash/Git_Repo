"""Main FastAPI application."""

import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import after environment setup
from src.database.models import get_db, init_db
from src.linkedin_api import (
    LinkedInAuthenticator, 
    LinkedInProfileAnalyzer,
    LinkedInPoster,
    LinkedInAnalytics
)
from src.profile_analyzer import ProfileAnalyzer
from src.content_generator import ContentGenerator
from src.scheduler import PostingScheduler

# Initialize FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "LinkedIn Profile Optimizer"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="AI-powered LinkedIn automation agent for profile growth"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
authenticator: LinkedInAuthenticator = None
scheduler: PostingScheduler = None


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global authenticator, scheduler
    
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized")
        
        # Initialize LinkedIn authenticator
        authenticator = LinkedInAuthenticator()
        if authenticator.authenticate():
            logger.info("LinkedIn authenticated successfully")
        else:
            logger.warning("LinkedIn authentication failed - running in demo mode")
        
        # Initialize scheduler
        scheduler = PostingScheduler()
        logger.info("Scheduler initialized")
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global scheduler
    
    if scheduler and scheduler.is_running:
        scheduler.stop()
        logger.info("Scheduler stopped")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "LinkedIn Profile Optimizer",
        "version": os.getenv("APP_VERSION", "1.0.0")
    }


# Profile endpoints
@app.get("/api/profile/info")
async def get_profile_info():
    """Get LinkedIn profile information."""
    if not authenticator or not authenticator.is_authenticated():
        return {"status": "error", "message": "Not authenticated - demo mode"}
    
    try:
        analyzer = LinkedInProfileAnalyzer(authenticator.client)
        profile = analyzer.get_profile()
        
        return {
            "status": "success",
            "data": profile
        }
    except Exception as e:
        logger.error(f"Error fetching profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profile/analysis")
async def get_profile_analysis():
    """Get detailed profile analysis."""
    try:
        if authenticator and authenticator.is_authenticated():
            linkedin_analyzer = LinkedInProfileAnalyzer(authenticator.client)
            profile = linkedin_analyzer.get_profile()
            experiences = linkedin_analyzer.get_experiences()
            skills = linkedin_analyzer.get_skills()
        else:
            # Demo data
            profile = {
                "firstName": "Demo",
                "lastName": "User",
                "headline": "Software Engineer | Tech Enthusiast",
                "about": "Passionate about technology",
                "connectionOfCount": 500,
                "followerCount": 1000
            }
            experiences = []
            skills = []
        
        # Analyze profile
        profile_analyzer = ProfileAnalyzer()
        profile_analysis = profile_analyzer.analyze_profile(profile)
        experience_analysis = profile_analyzer.analyze_experiences(experiences)
        expertise = profile_analyzer.identify_expertise_areas(experiences, skills)
        content_themes = profile_analyzer.identify_content_themes(experience_analysis)
        
        return {
            "status": "success",
            "profile": profile_analysis,
            "experiences": experience_analysis,
            "expertise_areas": expertise,
            "content_themes": content_themes
        }
    except Exception as e:
        logger.error(f"Error analyzing profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Content generation endpoints
@app.post("/api/content/generate")
async def generate_content(content_type: str = "insight"):
    """Generate AI-powered content."""
    try:
        if authenticator and authenticator.is_authenticated():
            linkedin_analyzer = LinkedInProfileAnalyzer(authenticator.client)
            profile = linkedin_analyzer.get_profile()
            experiences = linkedin_analyzer.get_experiences()
            skills = linkedin_analyzer.get_skills()
        else:
            # Demo data
            profile = {
                "firstName": "Demo",
                "lastName": "User",
                "headline": "Software Engineer | Tech Enthusiast",
                "connectionOfCount": 500,
                "followerCount": 1000
            }
            experiences = []
            skills = []
        
        # Analyze
        profile_analyzer = ProfileAnalyzer()
        profile_analysis = profile_analyzer.analyze_profile(profile)
        experience_analysis = profile_analyzer.analyze_experiences(experiences)
        expertise = profile_analyzer.identify_expertise_areas(experiences, skills)
        
        # Generate content
        context = {
            "user_info": profile_analysis,
            "experiences": experience_analysis.get("jobs", []),
            "expertise_areas": expertise,
            "major_achievements": experience_analysis.get("major_achievements", [])
        }
        
        generator = ContentGenerator()
        content = generator.generate_post(context, content_type)
        
        if content:
            return {
                "status": "success",
                "content": content,
                "type": content_type,
                "length": len(content)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate content")
            
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/content/generate-batch")
async def generate_batch_content(count: int = 5):
    """Generate multiple posts."""
    try:
        if authenticator and authenticator.is_authenticated():
            linkedin_analyzer = LinkedInProfileAnalyzer(authenticator.client)
            profile = linkedin_analyzer.get_profile()
            experiences = linkedin_analyzer.get_experiences()
            skills = linkedin_analyzer.get_skills()
        else:
            profile = {
                "firstName": "Demo",
                "lastName": "User",
                "headline": "Software Engineer | Tech Enthusiast",
                "connectionOfCount": 500
            }
            experiences = []
            skills = []
        
        # Analyze
        profile_analyzer = ProfileAnalyzer()
        profile_analysis = profile_analyzer.analyze_profile(profile)
        experience_analysis = profile_analyzer.analyze_experiences(experiences)
        expertise = profile_analyzer.identify_expertise_areas(experiences, skills)
        
        # Generate content
        context = {
            "user_info": profile_analysis,
            "experiences": experience_analysis.get("jobs", []),
            "expertise_areas": expertise,
            "major_achievements": experience_analysis.get("major_achievements", [])
        }
        
        generator = ContentGenerator()
        posts = generator.generate_multiple_posts(context, count)
        
        return {
            "status": "success",
            "posts": posts,
            "total": len(posts)
        }
            
    except Exception as e:
        logger.error(f"Error generating batch content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Scheduler endpoints
@app.get("/api/scheduler/status")
async def scheduler_status():
    """Get scheduler status."""
    if not scheduler:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")
    
    jobs = scheduler.get_jobs()
    return {
        "status": "running" if scheduler.is_running else "stopped",
        "jobs_count": len(jobs),
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None
            }
            for job in jobs
        ]
    }


@app.post("/api/scheduler/start")
async def start_scheduler():
    """Start the scheduler."""
    if not scheduler:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")
    
    try:
        scheduler.start()
        
        # Schedule tasks
        scheduler.schedule_daily_posting(post_daily_content)
        scheduler.schedule_profile_analysis(analyze_profile)
        scheduler.schedule_engagement_tracking(track_engagement)
        scheduler.schedule_content_generation(generate_daily_content)
        
        return {"status": "success", "message": "Scheduler started and tasks scheduled"}
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scheduler/stop")
async def stop_scheduler():
    """Stop the scheduler."""
    if not scheduler:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")
    
    try:
        scheduler.stop()
        return {"status": "success", "message": "Scheduler stopped"}
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions for scheduled tasks
def post_daily_content():
    """Post daily content to LinkedIn."""
    try:
        logger.info("=" * 70)
        logger.info("EXECUTING DAILY POSTING TASK")
        logger.info("=" * 70)
        
        db = next(get_db())
        
        try:
            # Get LinkedIn client
            client = authenticator.get_client() if authenticator else None
            poster = LinkedInPoster(client)
            
            # Generate fresh content
            context = {
                "user_info": {
                    "headline": "AI/ML Professional | Tech Leader",
                    "name": "LinkedIn User"
                },
                "experiences": [
                    {
                        "title": "Senior Software Engineer",
                        "company": "Tech Company",
                        "description": "Led development of scalable systems"
                    }
                ],
                "expertise_areas": ["Python", "Machine Learning", "Cloud Architecture", "Team Leadership"],
                "major_achievements": [
                    "Improved system performance by 40%",
                    "Led team of 5 engineers",
                    "Deployed ML model serving 1M users"
                ]
            }
            
            generator = ContentGenerator()
            content = generator.generate_post(context=context, content_type="insight")
            
            if content:
                # Post to LinkedIn
                post_id = poster.post_update(content)
                
                if post_id:
                    logger.info(f"✓ Successfully posted to LinkedIn!")
                    logger.info(f"  Post ID: {post_id}")
                    logger.info(f"  Content: {content[:60]}...")
                    
                    # Log to database
                    from src.database.models import ScheduleLog
                    log = ScheduleLog(
                        task_name="Daily LinkedIn Posting",
                        task_type="posting",
                        status="success",
                        message=f"Posted content - ID: {post_id}"
                    )
                    db.add(log)
                    db.commit()
                else:
                    logger.warning("Failed to post content")
            else:
                logger.warning("Failed to generate content")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in daily posting task: {str(e)}")
        import traceback
        traceback.print_exc()


def analyze_profile():
    """Analyze profile periodically."""
    try:
        logger.info("Executing profile analysis task")
        
        db = next(get_db())
        
        try:
            if authenticator and authenticator.is_authenticated():
                analyzer = LinkedInProfileAnalyzer(authenticator.get_client())
                profile = analyzer.get_profile()
                experiences = analyzer.get_experiences()
                skills = analyzer.get_skills()
                
                logger.info(f"✓ Profile analyzed: {profile.get('first_name')} {profile.get('last_name')}")
                logger.info(f"  Connections: {profile.get('connections')}")
                logger.info(f"  Followers: {profile.get('followers')}")
                logger.info(f"  Experiences: {len(experiences)}")
                logger.info(f"  Skills: {len(skills)}")
                
                # Log to database
                from src.database.models import ScheduleLog
                log = ScheduleLog(
                    task_name="Profile Analysis",
                    task_type="analysis",
                    status="success",
                    message=f"Analyzed {len(experiences)} experiences and {len(skills)} skills"
                )
                db.add(log)
                db.commit()
            else:
                logger.warning("LinkedIn not authenticated - skipping profile analysis")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in profile analysis task: {str(e)}")


def track_engagement():
    """Track engagement metrics."""
    try:
        logger.info("Executing engagement tracking task")
        
        db = next(get_db())
        
        try:
            if authenticator and authenticator.is_authenticated():
                analytics = LinkedInAnalytics(authenticator.get_client())
                profile_metrics = analytics.get_profile_metrics()
                
                logger.info(f"✓ Engagement tracked:")
                logger.info(f"  Connections: {profile_metrics.get('connections')}")
                logger.info(f"  Followers: {profile_metrics.get('followers')}")
                
                # Log to database
                from src.database.models import ScheduleLog
                log = ScheduleLog(
                    task_name="Engagement Tracking",
                    task_type="analytics",
                    status="success",
                    message=f"Connections: {profile_metrics.get('connections')}, Followers: {profile_metrics.get('followers')}"
                )
                db.add(log)
                db.commit()
            else:
                logger.warning("LinkedIn not authenticated - using demo metrics")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in engagement tracking task: {str(e)}")


def generate_daily_content():
    """Generate daily content."""
    try:
        logger.info("Executing content generation task")
        
        db = next(get_db())
        
        try:
            from src.database.models import GeneratedContent, User
            
            # Get or create user
            user = db.query(User).first()
            if not user:
                user = User(
                    email="agent@linkedin.com",
                    first_name="LinkedIn",
                    last_name="Agent",
                    headline="AI Agent | Content Creator"
                )
                db.add(user)
                db.commit()
            
            # Generate content
            context = {
                "user_info": {
                    "headline": "AI/ML Professional | Tech Leader",
                    "name": f"{user.first_name} {user.last_name}"
                },
                "experiences": [
                    {
                        "title": "Senior Software Engineer",
                        "company": "Tech Company"
                    }
                ],
                "expertise_areas": ["Python", "Machine Learning", "Cloud Architecture"],
                "major_achievements": ["Improved performance", "Led teams", "Shipped products"]
            }
            
            generator = ContentGenerator()
            content_types = ["insight", "tip", "achievement", "question", "reflection"]
            
            generated_count = 0
            for content_type in content_types:
                content = generator.generate_post(context=context, content_type=content_type)
                
                if content:
                    generated = GeneratedContent(
                        user_id=user.id,
                        content=content,
                        content_type=content_type,
                        status="generated",
                        engagement_score=0.0
                    )
                    db.add(generated)
                    generated_count += 1
            
            db.commit()
            
            logger.info(f"✓ Generated {generated_count} posts")
            
            # Log to database
            from src.database.models import ScheduleLog
            log = ScheduleLog(
                task_name="Content Generation",
                task_type="generation",
                status="success",
                message=f"Generated {generated_count} posts"
            )
            db.add(log)
            db.commit()
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in content generation task: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "False") == "True"
    )
