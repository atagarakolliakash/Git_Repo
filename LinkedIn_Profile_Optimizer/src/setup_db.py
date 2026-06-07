"""Setup database and initialize tables."""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.models import init_db
import logging

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def setup_database():
    """Initialize database tables."""
    try:
        init_db()
        logger.info("Database initialized successfully")
        print("✓ Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        print(f"✗ Error initializing database: {str(e)}")
        raise


if __name__ == "__main__":
    setup_database()
