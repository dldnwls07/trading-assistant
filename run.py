import os
import sys

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 1. Define paths (Absolute) using os.path for reliability
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Configure sys.path
# Ensure ROOT_DIR is in sys.path so we can import 'trading_assist' package located in ROOT_DIR
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 3. Import and run
try:
    from trading_assist.cli import main

    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Error: {e}")
    print("Failed to import 'trading_assist' package.")
    print(f"Ensure that '{ROOT_DIR}' contains the 'trading_assist' package.")
    sys.exit(1)
