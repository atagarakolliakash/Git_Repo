"""LinkedIn API integration and authentication."""

import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

try:
    from linkedin_api import Linkedin
except ImportError:
    Linkedin = None

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


class LinkedInAuthenticator:
    """Handles LinkedIn authentication and connection."""
    
    def __init__(self):
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.client: Optional[Linkedin] = None
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """Authenticate with LinkedIn using credentials."""
        try:
            if not self.email or not self.password:
                logger.error("LinkedIn credentials not configured in .env")
                return False
            
            if Linkedin is None:
                logger.error("linkedin-api library not installed")
                return False
            
            # Authenticate with LinkedIn
            self.client = Linkedin(self.email, self.password)
            self.authenticated = True
            
            logger.info(f"✓ Successfully authenticated with LinkedIn as {self.email}")
            return True
            
        except Exception as e:
            logger.error(f"LinkedIn authentication failed: {str(e)}")
            self.authenticated = False
            return False
    
    def is_authenticated(self) -> bool:
        """Check if authenticated and connection is active."""
        return self.authenticated and self.client is not None
    
    def get_client(self) -> Optional[Linkedin]:
        """Get the authenticated LinkedIn client."""
        if not self.is_authenticated():
            self.authenticate()
        return self.client


class LinkedInProfileAnalyzer:
    """Extracts and analyzes LinkedIn profile information."""
    
    def __init__(self, client: Optional[Linkedin]):
        self.client = client
        self.profile_data = None
    
    def get_profile(self) -> Dict[str, Any]:
        """Get current user's profile information."""
        try:
            if not self.client:
                logger.warning("No LinkedIn client available - returning demo data")
                return self._get_demo_profile()
            
            # Get profile data
            profile = self.client.get_profile()
            
            self.profile_data = {
                "first_name": profile.get("firstName", ""),
                "last_name": profile.get("lastName", ""),
                "headline": profile.get("headline", ""),
                "about": profile.get("summary", ""),
                "location": profile.get("location", {}).get("name", "") if profile.get("location") else "",
                "connections": profile.get("connectionOfCount", 0),
                "followers": profile.get("followerCount", 0),
                "profile_id": profile.get("linkedinId", ""),
            }
            
            logger.info(f"✓ Retrieved profile for {self.profile_data['first_name']} {self.profile_data['last_name']}")
            return self.profile_data
            
        except Exception as e:
            logger.warning(f"Error fetching profile (using demo data): {str(e)}")
            return self._get_demo_profile()
    
    def get_experiences(self) -> List[Dict[str, Any]]:
        """Get all job experiences."""
        try:
            if not self.client:
                logger.warning("No LinkedIn client available - returning demo experiences")
                return self._get_demo_experiences()
            
            experiences_data = self.client.get_profile()
            experiences = experiences_data.get("experience", [])
            
            formatted_experiences = []
            for exp in experiences:
                formatted_experiences.append({
                    "title": exp.get("title", ""),
                    "company": exp.get("companyName", ""),
                    "location": exp.get("location", ""),
                    "start_date": exp.get("startDate", {}).get("year", "") if exp.get("startDate") else "",
                    "end_date": exp.get("endDate", {}).get("year", "") if exp.get("endDate") else "Present",
                    "description": exp.get("description", ""),
                })
            
            logger.info(f"✓ Retrieved {len(formatted_experiences)} experiences")
            return formatted_experiences
            
        except Exception as e:
            logger.warning(f"Error fetching experiences (using demo data): {str(e)}")
            return self._get_demo_experiences()
    
    def get_skills(self) -> List[Dict[str, Any]]:
        """Get profile skills."""
        try:
            if not self.client:
                logger.warning("No LinkedIn client available - returning demo skills")
                return self._get_demo_skills()
            
            profile = self.client.get_profile()
            skills = profile.get("skills", [])
            
            formatted_skills = []
            for skill in skills:
                formatted_skills.append({
                    "name": skill.get("name", ""),
                    "endorsements": skill.get("endorsementCount", 0),
                })
            
            logger.info(f"✓ Retrieved {len(formatted_skills)} skills")
            return formatted_skills
            
        except Exception as e:
            logger.warning(f"Error fetching skills (using demo data): {str(e)}")
            return self._get_demo_skills()
    
    def get_connections_count(self) -> int:
        """Get number of connections."""
        try:
            profile = self.get_profile()
            return profile.get("connections", 0)
        except Exception as e:
            logger.error(f"Error fetching connections count: {str(e)}")
            return 0
    
    def _get_demo_profile(self) -> Dict[str, Any]:
        """Return demo profile for testing."""
        return {
            "first_name": "LinkedIn",
            "last_name": "User",
            "headline": "AI/ML Professional | Tech Leader",
            "about": "Passionate about technology, innovation, and growth",
            "location": "United States",
            "connections": 500,
            "followers": 1000,
            "profile_id": "demo_user",
        }
    
    def _get_demo_experiences(self) -> List[Dict[str, Any]]:
        """Return demo experiences for testing."""
        return [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Company",
                "location": "San Francisco, CA",
                "start_date": "2020",
                "end_date": "Present",
                "description": "Led development of scalable systems and mentored junior engineers",
            },
            {
                "title": "Software Engineer",
                "company": "Previous Corp",
                "location": "New York, NY",
                "start_date": "2018",
                "end_date": "2020",
                "description": "Built and maintained microservices architecture",
            }
        ]
    
    def _get_demo_skills(self) -> List[Dict[str, Any]]:
        """Return demo skills for testing."""
        return [
            {"name": "Python", "endorsements": 150},
            {"name": "Machine Learning", "endorsements": 120},
            {"name": "Cloud Architecture", "endorsements": 100},
            {"name": "Team Leadership", "endorsements": 80},
        ]


class LinkedInPoster:
    """Handles posting content to LinkedIn."""
    
    def __init__(self, client: Optional[Linkedin]):
        self.client = client
        self.posting_history: List[Dict[str, Any]] = []
        self.user_email = os.getenv("LINKEDIN_EMAIL", "user@linkedin.com")
    
    def post_update(self, content: str, media_url: Optional[str] = None) -> Optional[str]:
        """
        Post update to LinkedIn feed.
        
        **Note**: The linkedin-api library only supports read operations. 
        This method generates a simulated post URL and logs the action.
        To actually post on LinkedIn, use the official LinkedIn API or web interface.
        """
        try:
            if not content or len(content) < 10:
                logger.error("Content too short for posting (minimum 10 characters)")
                return None
            
            # Generate a unique post ID based on timestamp and content hash
            import hashlib
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            timestamp = int(datetime.now().timestamp() * 1000)
            post_id = f"activity:{timestamp}_{content_hash}"
            
            # Create simulated post URL (LinkedIn format)
            # Real posts would be at: https://www.linkedin.com/feed/update/urn:li:activity:6xxxxxxxxxxxxx/
            post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
            
            self.posting_history.append({
                "post_id": post_id,
                "post_url": post_url,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "status": "simulated",
                "note": "Simulated post - linkedin-api library supports read-only operations"
            })
            
            logger.info(f"✓ Post generated (simulated mode)")
            logger.info(f"  Post ID: {post_id}")
            logger.info(f"  Post URL: {post_url}")
            logger.info(f"  Content preview: {content[:50]}...")
            logger.warning(f"  NOTE: This is a simulated post. To post on LinkedIn:")
            logger.warning(f"  1. Use LinkedIn official web interface: https://www.linkedin.com")
            logger.warning(f"  2. Or use official LinkedIn API: https://learn.microsoft.com/en-us/linkedin/")
            logger.warning(f"  3. Copy this content and post manually")
            
            return post_id
                
        except Exception as e:
            logger.error(f"Error in post generation: {str(e)}")
            return None
    
    def get_post_url(self, post_id: str) -> str:
        """Get the LinkedIn post URL for a given post ID."""
        return f"https://www.linkedin.com/feed/update/{post_id}/"
    
    def get_posting_history(self) -> List[Dict[str, Any]]:
        """Get all posts created."""
        return self.posting_history
    
    def get_feed(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get current feed posts."""
        try:
            if not self.client:
                logger.warning("No LinkedIn client available - returning empty feed")
                return []
            
            # Get feed from LinkedIn
            feed = self.client.get_feed()
            
            formatted_feed = []
            for post in feed[:limit]:
                formatted_feed.append({
                    "post_id": post.get("id", ""),
                    "author": post.get("actor", {}).get("name", ""),
                    "content": post.get("content", ""),
                    "timestamp": post.get("timestamp", ""),
                    "likes": post.get("likeCount", 0),
                    "comments": post.get("commentCount", 0),
                })
            
            logger.info(f"✓ Retrieved {len(formatted_feed)} feed posts")
            return formatted_feed
            
        except Exception as e:
            logger.error(f"Error fetching feed: {str(e)}")
            return []
    
    def get_posting_history(self) -> List[Dict[str, Any]]:
        """Get history of posts made by this agent."""
        return self.posting_history


class LinkedInAnalytics:
    """Track and analyze LinkedIn engagement metrics."""
    
    def __init__(self, client: Optional[Linkedin]):
        self.client = client
        self.metrics_cache: Dict[str, Any] = {}
    
    def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific post."""
        try:
            if not self.client:
                logger.warning("No LinkedIn client - returning demo analytics")
                return {
                    "post_id": post_id,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "impressions": 0,
                    "engagement_rate": 0.0,
                    "status": "demo"
                }
            
            # Try to get real analytics from LinkedIn
            try:
                post_data = self.client.get_post(post_id)
                
                likes = post_data.get("likeCount", 0)
                comments = post_data.get("commentCount", 0)
                shares = post_data.get("shareCount", 0)
                impressions = post_data.get("impressionCount", 0)
                
                engagement_rate = (likes + comments + shares) / max(impressions, 1) if impressions > 0 else 0
                
                analytics = {
                    "post_id": post_id,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "impressions": impressions,
                    "engagement_rate": round(engagement_rate, 4),
                    "status": "live"
                }
                
                self.metrics_cache[post_id] = analytics
                logger.info(f"✓ Retrieved analytics for post {post_id}")
                return analytics
                
            except Exception as api_error:
                logger.warning(f"Could not fetch real analytics: {str(api_error)}")
                # Return cached or demo data
                return self.metrics_cache.get(post_id, {
                    "post_id": post_id,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "impressions": 0,
                    "engagement_rate": 0.0,
                    "status": "cached"
                })
                
        except Exception as e:
            logger.error(f"Error fetching post analytics: {str(e)}")
            return {}
    
    def get_profile_metrics(self) -> Dict[str, Any]:
        """Get overall profile metrics."""
        try:
            if not self.client:
                logger.warning("No LinkedIn client - returning demo profile metrics")
                return {
                    "connections": 0,
                    "followers": 0,
                    "headline": "",
                    "status": "demo"
                }
            
            profile = self.client.get_profile()
            
            metrics = {
                "connections": profile.get("connectionOfCount", 0),
                "followers": profile.get("followerCount", 0),
                "headline": profile.get("headline", ""),
                "profile_id": profile.get("linkedinId", ""),
                "name": f"{profile.get('firstName', '')} {profile.get('lastName', '')}",
                "status": "live"
            }
            
            logger.info(f"✓ Retrieved profile metrics for {metrics['name']}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error fetching profile metrics: {str(e)}")
            return {}
    
    def track_engagement(self, post_id: str, likes: int = 0, comments: int = 0, shares: int = 0) -> bool:
        """Track engagement metrics for a post."""
        try:
            engagement = {
                "post_id": post_id,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "timestamp": datetime.now().isoformat(),
                "total_engagement": likes + comments + shares
            }
            
            self.metrics_cache[post_id] = engagement
            logger.info(f"✓ Tracked engagement for post {post_id}: {likes}L {comments}C {shares}S")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking engagement: {str(e)}")
            return False

