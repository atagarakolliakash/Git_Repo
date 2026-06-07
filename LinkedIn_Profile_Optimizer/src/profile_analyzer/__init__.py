"""Profile analysis and job history parsing."""

import logging
import os
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ProfileAnalyzer:
    """Analyzes LinkedIn profile and extracts key information."""
    
    def __init__(self, db: Any = None):
        self.db = db
    
    def analyze_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze profile and extract key insights."""
        analysis = {
            "name": f"{profile_data.get('firstName', '')} {profile_data.get('lastName', '')}".strip(),
            "headline": profile_data.get("headline", ""),
            "location": profile_data.get("locationName", ""),
            "summary": profile_data.get("about", ""),
            "connections": profile_data.get("connectionOfCount", 0),
            "followers": profile_data.get("followerCount", 0),
            "key_themes": [],
            "expertise_areas": [],
            "career_progression": []
        }
        return analysis
    
    def analyze_experiences(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze job experiences to extract responsibilities and achievements."""
        analysis = {
            "total_experience_years": 0,
            "jobs": [],
            "key_responsibilities": [],
            "major_achievements": [],
            "industry_focus": [],
            "role_progression": []
        }
        
        for exp in experiences:
            job_analysis = {
                "title": exp.get("title", ""),
                "company": exp.get("companyName", ""),
                "duration": {
                    "start": exp.get("dateRange", {}).get("start", {}),
                    "end": exp.get("dateRange", {}).get("end", {})
                },
                "location": exp.get("locationName", ""),
                "description": exp.get("description", ""),
                "extracted_responsibilities": self._extract_responsibilities(exp),
                "extracted_achievements": self._extract_achievements(exp)
            }
            analysis["jobs"].append(job_analysis)
        
        analysis["key_responsibilities"] = self._aggregate_responsibilities(analysis["jobs"])
        analysis["major_achievements"] = self._aggregate_achievements(analysis["jobs"])
        
        return analysis
    
    def _extract_responsibilities(self, experience: Dict[str, Any]) -> List[str]:
        """Extract responsibilities from experience description."""
        description = experience.get("description", "")
        if not description:
            return []
        
        responsibilities = []
        lines = description.split("\n")
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                responsibilities.append(line)
        
        return responsibilities[:5]
    
    def _extract_achievements(self, experience: Dict[str, Any]) -> List[str]:
        """Extract achievements from experience description."""
        description = experience.get("description", "")
        if not description:
            return []
        
        achievements = []
        keywords = ["achieved", "increased", "improved", "led", "managed", "developed", "launched", "grew"]
        
        lines = description.split("\n")
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                achievements.append(line.strip())
        
        return achievements[:5]
    
    def _aggregate_responsibilities(self, jobs: List[Dict[str, Any]]) -> List[str]:
        """Aggregate key responsibilities across all jobs."""
        all_responsibilities = []
        for job in jobs:
            all_responsibilities.extend(job.get("extracted_responsibilities", []))
        
        return list(dict.fromkeys(all_responsibilities))[:10]
    
    def _aggregate_achievements(self, jobs: List[Dict[str, Any]]) -> List[str]:
        """Aggregate major achievements across all jobs."""
        all_achievements = []
        for job in jobs:
            all_achievements.extend(job.get("extracted_achievements", []))
        
        return list(dict.fromkeys(all_achievements))[:10]
    
    def identify_expertise_areas(self, experiences: List[Dict[str, Any]], skills: List[Dict[str, Any]]) -> List[str]:
        """Identify core expertise areas from experiences and skills."""
        expertise = []
        
        for skill in skills:
            skill_name = skill.get("name", "") or skill.get("title", "")
            if skill_name:
                expertise.append(skill_name)
        
        title_keywords = {}
        for exp in experiences:
            title = exp.get("title", "").lower()
            words = title.split()
            for word in words:
                if word in title_keywords:
                    title_keywords[word] += 1
                else:
                    title_keywords[word] = 1
        
        sorted_keywords = sorted(title_keywords.items(), key=lambda x: x[1], reverse=True)
        expertise.extend([word for word, count in sorted_keywords[:5]])
        
        return list(dict.fromkeys(expertise))[:15]
    
    def identify_content_themes(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify potential content themes based on profile analysis."""
        themes = []
        
        jobs = analysis.get("jobs", [])
        
        common_keywords = {
            "engineer": ["technical", "problem-solving", "innovation"],
            "manager": ["leadership", "team building", "strategy"],
            "sales": ["growth", "relationships", "success"],
            "product": ["innovation", "user experience", "strategy"],
            "designer": ["creativity", "design thinking", "user-centric"],
            "analyst": ["insights", "data", "strategy"],
            "consultant": ["problem-solving", "strategy", "change"],
            "developer": ["technical", "innovation", "code quality"]
        }
        
        for job in jobs:
            title_lower = job.get("title", "").lower()
            for keyword, suggested_themes in common_keywords.items():
                if keyword in title_lower:
                    themes.extend(suggested_themes)
        
        return list(dict.fromkeys(themes))

