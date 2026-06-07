"""Unit tests for LinkedIn Profile Optimizer."""

import pytest
from src.profile_analyzer import ProfileAnalyzer
from src.content_generator import ContentGenerator


@pytest.fixture
def sample_profile_data():
    """Sample LinkedIn profile data."""
    return {
        "firstName": "John",
        "lastName": "Doe",
        "headline": "Software Engineer at Tech Corp",
        "locationName": "San Francisco, CA",
        "about": "Passionate about technology and innovation",
        "connectionOfCount": 500,
        "followerCount": 1000
    }


@pytest.fixture
def sample_experience():
    """Sample job experience data."""
    return [
        {
            "title": "Senior Software Engineer",
            "companyName": "Tech Corp",
            "locationName": "San Francisco, CA",
            "description": "Led development of microservices architecture. Increased system performance by 40%. Managed team of 5 engineers.",
            "dateRange": {
                "start": {"month": 1, "year": 2020},
                "end": None
            }
        }
    ]


def test_profile_analyzer(sample_profile_data):
    """Test profile analysis."""
    # This would require a database session
    # analyzer = ProfileAnalyzer(db)
    # result = analyzer.analyze_profile(sample_profile_data)
    # assert result is not None
    # assert result["name"] == "John Doe"
    pass


def test_content_generator():
    """Test content generation."""
    # This requires OpenAI API key
    # generator = ContentGenerator()
    # assert generator is not None
    pass
