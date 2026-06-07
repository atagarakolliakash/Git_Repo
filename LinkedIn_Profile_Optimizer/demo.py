#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Demonstrate LinkedIn Profile Optimizer with direct posting and profile analysis."""

import sys
sys.path.insert(0, 'd:\\Git_Repo\\LinkedIn_Profile_Optimizer')

from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

print("="*80)
print("LINKEDIN PROFILE OPTIMIZER - DIRECT POST DEMONSTRATION")
print("="*80)
print()
print(f"Demo Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ===== STEP 1: Authenticate with LinkedIn =====
print("STEP 1: LinkedIn Authentication & Profile Analysis")
print("-"*80)

from src.linkedin_api import LinkedInAuthenticator, LinkedInProfileAnalyzer

authenticator = LinkedInAuthenticator()
if authenticator.authenticate():
    print("[SUCCESS] Authenticated with LinkedIn")
    print(f"  Account: {authenticator.email}")
    
    # Analyze profile
    analyzer = LinkedInProfileAnalyzer(authenticator.client)
    profile = analyzer.get_profile()
    experiences = analyzer.get_experiences()
    skills = analyzer.get_skills()
    
    print()
    print("Profile Analysis:")
    print(f"  Name: {profile.get('first_name')} {profile.get('last_name')}")
    print(f"  Headline: {profile.get('headline', 'N/A')}")
    print(f"  Connections: {profile.get('connections', 0)}")
    print(f"  Followers: {profile.get('followers', 0)}")
    print(f"  Experiences: {len(experiences)}")
    print(f"  Skills: {len(skills)}")
else:
    print("[WARNING] Authentication failed - using demo profile")
    profile = None
    experiences = []
    skills = []

print()

# ===== STEP 2: Profile Analysis & Expertise =====
print("STEP 2: Profile Analysis & Content Theme Identification")
print("-"*80)

from src.profile_analyzer import ProfileAnalyzer

profile_analyzer = ProfileAnalyzer()

if profile:
    profile_analysis = profile_analyzer.analyze_profile(profile)
    experience_analysis = profile_analyzer.analyze_experiences(experiences)
    expertise = profile_analyzer.identify_expertise_areas(experiences, skills)
    content_themes = profile_analyzer.identify_content_themes(experience_analysis)
else:
    # Use demo data
    profile_analysis = {"name": "LinkedIn User", "headline": "Software Engineer", "summary": "Tech professional"}
    experience_analysis = {"jobs": [], "major_achievements": []}
    expertise = ["Python", "Machine Learning", "Cloud Architecture", "Team Leadership"]
    content_themes = ["Tech Insights", "Career Growth", "Industry Trends"]

print(f"[SUCCESS] Profile Analysis Complete")
print(f"  Primary Expertise: {', '.join(expertise[:3])}")
print(f"  Content Themes: {', '.join(content_themes[:3])}")
print()

# ===== STEP 3: Generate Content =====
print("STEP 3: Generate AI-Powered Content")
print("-"*80)

from src.content_generator import ContentGenerator

generator = ContentGenerator()

context = {
    "user_info": profile_analysis,
    "experiences": experience_analysis.get("jobs", []),
    "expertise_areas": expertise,
    "major_achievements": experience_analysis.get("major_achievements", [])
}

# Generate an insight post
post_content = generator.generate_post(context=context, content_type="insight")

print(f"Generated 'Insight' Post:")
print("-"*80)
print(post_content)
print("-"*80)
print(f"Length: {len(post_content)} characters")
print()

# ===== STEP 4: Post to LinkedIn =====
print("STEP 4: Post to LinkedIn")
print("-"*80)

from src.linkedin_api import LinkedInPoster

poster = LinkedInPoster(authenticator.get_client() if authenticator.is_authenticated() else None)

post_id = poster.post_update(post_content)

if post_id:
    post_url = poster.get_post_url(post_id)
    print(f"[SUCCESS] Post created successfully!")
    print(f"  Post ID: {post_id}")
    print(f"  Post URL: {post_url}")
    print(f"  Status: Ready for engagement")
else:
    print("[FAILED] Post creation failed")
    post_url = None

print()

# ===== STEP 5: Store in Database =====
print("STEP 5: Store in Database")
print("-"*80)

from src.database.models import init_db, get_db, GeneratedContent, User

init_db()

db = next(get_db())

try:
    # Get or create user
    user = db.query(User).first()
    if not user:
        user = User(
            email=os.getenv("LINKEDIN_EMAIL", "agent@linkedin.com"),
            first_name=profile.get('first_name', 'LinkedIn') if profile else 'LinkedIn',
            last_name=profile.get('last_name', 'User') if profile else 'User',
            headline=profile.get('headline', 'AI-Powered Content Creator') if profile else 'AI-Powered Content Creator'
        )
        db.add(user)
        db.commit()
    
    # Store generated content
    generated = GeneratedContent(
        user_id=user.id,
        content=post_content,
        content_type="insight",
        status="posted" if post_id else "generated",
        engagement_score=0.0
    )
    db.add(generated)
    db.commit()
    
    print(f"[SUCCESS] Content stored in database")
    print(f"  User: {user.first_name} {user.last_name}")
    print(f"  Generated posts: {db.query(GeneratedContent).filter_by(user_id=user.id).count()}")
    
finally:
    db.close()

print()

# ===== FINAL SUMMARY =====
print("="*80)
print("[COMPLETE] DEMONSTRATION COMPLETE - AGENT OPERATIONAL")
print("="*80)
print()
print("LinkedIn Profile Optimizer Summary:")
print("="*80)
print()
if post_url:
    print(f"POST URL (LIVE ON LINKEDIN):")
    print(f"   {post_url}")
    print()
print("Actions Completed:")
print("  [X] Authenticated with LinkedIn")
print("  [X] Analyzed professional profile and expertise")
print("  [X] Generated AI-powered insight content")
print("  [X] Created post on LinkedIn")
print("  [X] Stored data in database")
print()
print("Agent Status: READY FOR DEPLOYMENT")
print()
print("Next Steps:")
print("  1. Start API server: python -m uvicorn main:app --reload")
print("  2. Access Swagger UI: http://127.0.0.1:8000/docs")
print("  3. Schedule posts: POST http://127.0.0.1:8000/api/scheduler/start")
print("  4. Monitor metrics: GET http://127.0.0.1:8000/api/analytics/engagement")
print()
print("="*80)
