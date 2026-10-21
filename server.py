"""
server.py - Deprecated entry point (Forwarding to app.py)
---------------------------------------------------------
This file is now unified with `app.py`.
You can run directly:
    python app.py
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import main

if __name__ == "__main__":
    main()

