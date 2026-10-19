"""
Sales Incentive Calculation & Dashboard System - Server
--------------------------------------------------------
Unified entry point to run the backend API and frontend web dashboard
from within this directory.

Usage:
    python server.py
    python server.py --port 5000 --host 127.0.0.1
    python server.py --no-debug
"""
import argparse
import os
import sys
from pathlib import Path

# Ensure incentive_website directory is at the root of sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import app


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the Sales Incentive Calculation Platform server (Backend & Frontend)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("HOST", "127.0.0.1"),
        help="Host address to bind the server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 5000)),
        help="Port to listen on (default: 5000)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.environ.get("DEBUG", "true").lower() in ("true", "1", "t", "yes"),
        help="Run server in debug mode with auto-reload (default: True)",
    )
    parser.add_argument(
        "--no-debug",
        action="store_false",
        dest="debug",
        help="Disable debug mode",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    banner = "=" * 70
    print(banner)
    print(" DKT Sales Incentive Calculation & Dashboard System")
    print(" Backend & Frontend Server")
    print(banner)
    print(f" -> Web Dashboard (Frontend): http://{args.host}:{args.port}/")
    print(f" -> Incentive Dashboard:      http://{args.host}:{args.port}/incentive/")
    print(f" -> Health Check:             http://{args.host}:{args.port}/health")
    print(f" -> Debug Mode:               {args.debug}")
    print(banner)
    print("Press Ctrl+C to stop the server.\n")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
