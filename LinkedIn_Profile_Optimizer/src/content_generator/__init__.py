"""AI-powered content generation for LinkedIn posts."""

import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generates AI-powered LinkedIn content."""
    
    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.tone = os.getenv("TONE", "professional")
        self.min_length = int(os.getenv("CONTENT_MIN_LENGTH", 50))
        self.max_length = int(os.getenv("CONTENT_MAX_LENGTH", 3000))
    
    def generate_post(self, 
                     context: Dict[str, Any],
                     content_type: str = "insight") -> Optional[str]:
        """Generate a LinkedIn post based on context."""
        try:
            content = self._generate_content(context, content_type)
            
            if content and self.min_length <= len(content) <= self.max_length:
                logger.info(f"Generated {content_type} post successfully")
                return content
            else:
                logger.warning(f"Generated content length out of range")
                return None
                
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return None
    
    def generate_multiple_posts(self,
                               context: Dict[str, Any],
                               count: int = 5) -> List[Dict[str, str]]:
        """Generate multiple diverse posts."""
        content_types = ["insight", "tip", "achievement", "question", "reflection"]
        posts = []
        
        for i in range(count):
            content_type = content_types[i % len(content_types)]
            content = self.generate_post(context, content_type)
            
            if content:
                posts.append({
                    "content": content,
                    "type": content_type,
                    "length": len(content)
                })
        
        return posts
    
    def _generate_content(self, context: Dict[str, Any], content_type: str) -> Optional[str]:
        """Generate content based on type."""
        
        user_info = context.get("user_info", {})
        experiences = context.get("experiences", [])
        expertise = context.get("expertise_areas", [])
        achievements = context.get("major_achievements", [])
        
        templates = {
            "insight": self._insight_template(user_info, experiences, expertise),
            "tip": self._tip_template(user_info, experiences),
            "achievement": self._achievement_template(user_info, achievements),
            "question": self._question_template(user_info, expertise),
            "reflection": self._reflection_template(user_info, experiences)
        }
        
        return templates.get(content_type, templates["insight"])
    
    def _insight_template(self, user_info: Dict, experiences: List, expertise: List) -> str:
        """Create insight post template."""
        headline = user_info.get("headline", "professional")
        job_title = experiences[0].get("title", "your role") if experiences else "your role"
        
        insights = [
            f"[INSIGHT] After working in {job_title}, here's what I've learned:\n\nThe key to success is continuous learning and adaptation. In this fast-paced landscape, staying ahead means regularly updating your skills and being open to new perspectives.",
            f"[INSIGHT] One insight from my {job_title} experience:\n\nCollaboration trumps individual brilliance. The best results come from diverse teams working toward a common goal.",
            f"[INSIGHT] The {job_title} field is evolving rapidly.\n\nWhat's working today might be outdated tomorrow. Focus on fundamentals and be ready to pivot.",
            f"[INSIGHT] In my journey as a {job_title}, I've discovered:\n\nWhat sets top performers apart isn't just technical skills—it's emotional intelligence and communication.",
        ]
        
        return insights[len(insights) % 4]
    
    def _tip_template(self, user_info: Dict, experiences: List) -> str:
        """Create tip post template."""
        job_title = experiences[0].get("title", "professional") if experiences else "professional"
        
        tips = [
            f"[TIP] Tip for aspiring {job_title}s:\n\nAlways document your achievements. Don't assume others know what you've accomplished. Regular updates with stakeholders save you during review time.",
            f"[TIP] Here's what I wish I knew when starting my {job_title} career:\n\nNetworking is not just about finding jobs. It's about building genuine relationships with people in your field.",
            f"[TIP] Quick productivity tip:\n\nBreak your day into blocks. 90 minutes of focused work + 15 minutes of rest. Your brain will thank you, and so will your output.",
            f"[TIP] In today's digital world:\n\nSet boundaries. Constant notifications kill deep work. Turn off notifications during your peak productivity hours.",
        ]
        
        return tips[len(tips) % 4]
    
    def _achievement_template(self, user_info: Dict, achievements: List) -> str:
        """Create achievement post template."""
        achievement = achievements[0] if achievements else "completed an important project"
        
        achievement_posts = [
            f"[ACHIEVEMENT] Excited to share that {achievement}!\n\nThis wouldn't have been possible without the amazing support from my team and mentors. Grateful for every learning experience along the way. #Growth #Achievement",
            f"[ACHIEVEMENT] Milestone reached: {achievement}\n\nThanks to everyone who believed in this vision and worked tirelessly to make it reality. Can't wait for what's next!",
            f"[ACHIEVEMENT] Just accomplished something I'm really proud of: {achievement}\n\nThe journey was challenging, but that's what made it worthwhile. Here's to continuous improvement!",
        ]
        
        return achievement_posts[len(achievement_posts) % 3]
    
    def _question_template(self, user_info: Dict, expertise: List) -> str:
        """Create question post template."""
        expertise_str = ", ".join(expertise[:2]) if expertise else "your field"
        
        questions = [
            f"[QUESTION] Question for the {expertise_str} community:\n\nWhat's the most valuable skill you've developed in your career? I'd love to hear your thoughts!",
            f"[QUESTION] I'm curious: What's one challenge you're facing in {expertise_str} right now?\n\nLet's learn from each other. Drop your thoughts in the comments!",
            f"[DISCUSSION] Discussion starter:\n\nHow do you stay updated with the latest trends in {expertise_str}? Would love to exchange resources and strategies!",
        ]
        
        return questions[len(questions) % 3]
    
    def _reflection_template(self, user_info: Dict, experiences: List) -> str:
        """Create reflection post template."""
        if len(experiences) > 1:
            journey = f"from {experiences[-1].get('title', 'my start')} to {experiences[0].get('title', 'today')}"
        else:
            journey = "my career journey"
        
        reflections = [
            f"[REFLECTION] Reflecting on {journey}:\n\nThe most valuable lesson? Embrace the discomfort of growth. Every challenge was actually an opportunity in disguise. Grateful for how far I've come!",
            f"[REFLECTION] Career reflection:\n\nSuccess isn't a destination—it's a continuous journey of learning and growth. Excited for the next chapter! #CareerGrowth",
            f"[REFLECTION] {journey} has taught me that resilience matters more than talent alone.\n\nHere's to everyone working toward their dreams. Keep going!",
        ]
        
        return reflections[len(reflections) % 3]

