# LinkedIn Profile Optimizer - Quick Start Guide

## Installation (First Time Only)

```bash
# 1. Navigate to project
cd LinkedIn_Profile_Optimizer

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure credentials
cp .env.example .env
# Edit .env with your LinkedIn email and password
```

## Running the Agent

### Option 1: Generate Content Now (Recommended for Testing)

```bash
python demo.py
```

**Output:**
- Authenticates with LinkedIn
- Analyzes your profile
- Generates professional post
- Saves to database
- Displays content ready to copy-paste

### Option 2: Start API Server (For Automation)

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Access:**
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

### Option 3: Schedule Automatic Posting (Advanced)

1. Start API server (Option 2 above)
2. In separate terminal:
```bash
curl -X POST http://localhost:8000/api/scheduler/start
```
3. Check status:
```bash
curl http://localhost:8000/api/scheduler/status
```

## Project Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application |
| `demo.py` | One-shot demonstration |
| `requirements.txt` | Python dependencies |
| `.env` | Your credentials (DO NOT commit) |
| `.env.example` | Template for .env |
| `README.md` | Full documentation |
| `src/` | Application source code |
| `tests/` | Unit tests |

## Environment Variables (.env)

```env
# REQUIRED
LINKEDIN_EMAIL=your-email@gmail.com
LINKEDIN_PASSWORD=your-password

# OPTIONAL
POSTING_TIME=22:00
POSTING_TIMEZONE=UTC
MAX_POSTS_PER_DAY=1
TONE=professional
LOG_LEVEL=INFO
```

## Common Commands

```bash
# Run demo
python demo.py

# Start API
python -m uvicorn main:app --reload

# Generate single post
curl http://localhost:8000/api/content/generate

# Generate 5 posts
curl http://localhost:8000/api/content/generate-batch

# View profile analysis
curl http://localhost:8000/api/profile/analysis

# Start scheduler
curl -X POST http://localhost:8000/api/scheduler/start

# Stop scheduler
curl -X POST http://localhost:8000/api/scheduler/stop

# Check scheduler status
curl http://localhost:8000/api/scheduler/status
```

## Troubleshooting

**Port 8000 already in use:**
```bash
python -m uvicorn main:app --reload --port 8001
```

**Module not found:**
```bash
pip install -r requirements.txt
```

**Authentication failed:**
- Check `.env` file has correct credentials
- Verify email/password are correct
- Ensure 2FA is not blocking automated login

**Database error:**
```bash
rm linkedin_agent.db
```

## Tips

✓ Always review generated content before posting
✓ Start with `demo.py` to test
✓ Use small batch sizes initially
✓ Monitor engagement and adjust
✓ Keep `.env` file secure and never commit it
✓ Enable logging for debugging: set `LOG_LEVEL=DEBUG` in .env

## Next Steps

1. ✓ Install dependencies
2. ✓ Configure .env
3. Run `python demo.py` to test
4. Review generated content
5. Manually post to LinkedIn
6. Gradually enable automation

---

**Questions?** Check README.md for full documentation.
