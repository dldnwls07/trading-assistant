"""
Centralized configuration for the Trading Assistant application.
"""
from pathlib import Path

# --- Directories ---
# Base directory of the project
PROJECT_ROOT = Path(__file__).parent.parent

# Directory for storing fetched data (e.g., CSV files)
DATA_DIR = PROJECT_ROOT / "data"

# Directory for storing generated charts
CHART_DIR = PROJECT_ROOT / "charts"


# --- Analysis Parameters ---
# Default short-term moving average window
DEFAULT_MA_SHORT_WINDOW = 50

# Default long-term moving average window
DEFAULT_MA_LONG_WINDOW = 200


def init_dirs():
    """Create necessary directories if they don't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    CHART_DIR.mkdir(exist_ok=True)

