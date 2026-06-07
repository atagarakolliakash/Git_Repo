# LinkedIn Profile Optimizer

An intelligent automation agent that analyzes your LinkedIn profile and generates AI-powered professional content for daily posting.

## Key Features

- **LinkedIn Authentication** - Secure credential-based authentication
- **Profile Analysis** - Extracts skills, experiences, and expertise areas
- **AI Content Generation** - Creates diverse posts (insights, tips, achievements, questions)
- **Automated Scheduling** - Daily posting at configured times
- **Analytics Tracking** - Monitor engagement and post performance
- **Database Persistence** - SQLite for historical data storage

## Quick Start

### Prerequisites

- Python 3.12+
- LinkedIn account with email and password
- pip package manager

### 1. Install & Configure

```bash
# Clone and navigate
cd LinkedIn_Profile_Optimizer

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your LinkedIn credentials
```

### 2. Run Immediately

Generate a post right now without scheduling:

```bash
python demo.py
```

This will:
- Authenticate with LinkedIn
- Analyze your profile
- Generate professional content
- Save to database
- Output ready-to-post content

### 3. Or Start API Server

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Access at: `http://localhost:8000/docs` (Swagger UI)

## Project Structure

```
LinkedIn_Profile_Optimizer/
├── main.py                    # FastAPI application
├── demo.py                    # One-shot demonstration
├── requirements.txt           # Dependencies
├── .env                       # Configuration (local)
├── .env.example               # Configuration template
├── README.md                  # Documentation
│
├── src/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── models.py          # SQLAlchemy ORM models
│   │
│   ├── linkedin_api/
│   │   └── __init__.py        # LinkedIn API wrapper
│   │
│   ├── profile_analyzer/
│   │   └── __init__.py        # Profile analysis engine
│   │
│   ├── content_generator/
│   │   └── __init__.py        # AI content generation
│   │
│   └── scheduler/
│       └── __init__.py        # APScheduler integration
│
├── tests/
│   └── test_agent.py          # Unit tests
│
└── .github/
    └── copilot-instructions.md
```

## Configuration

Edit `.env` with your settings:

```env
# LinkedIn (Required)
LINKEDIN_EMAIL=your-email@gmail.com
LINKEDIN_PASSWORD=your-password

# OpenAI (Optional)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# Posting Schedule
POSTING_TIME=22:00              # 24-hour format
POSTING_TIMEZONE=UTC
MAX_POSTS_PER_DAY=1

# Content
TONE=professional              # professional, casual, thought_leader
CONTENT_MIN_LENGTH=50
CONTENT_MAX_LENGTH=3000

# Logging
LOG_LEVEL=INFO
```

## Usage

### Generate Content Now
```bash
python demo.py
```

### Start API Server
```bash
python -m uvicorn main:app --reload
```

### API Endpoints

**Profile**
- `GET /api/profile/info` - Get profile information
- `GET /api/profile/analysis` - Detailed analysis

**Content**
- `POST /api/content/generate` - Generate single post
- `POST /api/content/generate-batch` - Generate 5 posts

**Scheduler**
- `POST /api/scheduler/start` - Enable automatic posting
- `POST /api/scheduler/stop` - Disable automatic posting
- `GET /api/scheduler/status` - Check scheduler status

**Other**
- `GET /health` - API health check
- `GET /docs` - Swagger UI (interactive)

## Content Generation

The agent generates posts based on:
- Your job titles and responsibilities
- Professional skills and expertise
- Industry insights and trends
- Career achievements and milestones

Post types:
- **Insights**: Industry observations and learning
- **Tips**: Practical career and professional advice
- **Achievements**: Milestone announcements
- **Questions**: Engagement-focused community discussions
- **Reflections**: Career growth and personal learnings

## Security & Best Practices

⚠️ **Important**

- Never commit `.env` to version control
- Keep credentials secure and private
- Review generated content before posting
- Comply with LinkedIn Terms of Service
- Start with manual posting before full automation
- Monitor content performance and adjust strategy

## Troubleshooting

**Authentication Failed**
- Verify LinkedIn email/password in `.env`
- Check if 2FA is enabled on account
- Ensure credentials are correct

**API Won't Start**
- Check if port 8000 is available: `lsof -i :8000`
- Verify Python version: `python --version`

**Database Issues**
```bash
# Reinitialize database
rm linkedin_agent.db
python -c "from src.database.models import init_db; init_db()"
```

## Technology Stack

- **Framework**: FastAPI + Uvicorn
- **Database**: SQLite + SQLAlchemy
- **Scheduling**: APScheduler
- **LinkedIn**: linkedin-api 2.0
- **Language**: Python 3.12

## License

Proprietary - All rights reserved

## Status

✓ Production Ready | ✓ Tested | ✓ Ready for Deployment
