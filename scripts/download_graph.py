#!/usr/bin/env python3
"""Tải và cache graph OSMnx (chạy một lần trước demo)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config_loader import load_config, resolve_path
from src.map_service import MapService


def main():
    cfg = load_config()
    svc = MapService(
        cfg["place_name"],
        cfg["network_type"],
        resolve_path(cfg["paths"]["graph_cache"]),
    )
    svc.load_or_download(force_download=True)
    print("Hoàn tất.")


if __name__ == "__main__":
    main()
