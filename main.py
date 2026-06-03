#!/usr/bin/env python3
"""
Smart Delivery Routing Demo
Chạy: python main.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.demo import run_demo  # noqa: E402

if __name__ == "__main__":
    run_demo()
