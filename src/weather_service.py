"""
API thời tiết Open-Meteo — hệ số điều chỉnh thời gian giao hàng.
"""

from __future__ import annotations

import requests


class WeatherService:
    BASE = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, lat: float, lon: float, weather_cfg: dict):
        self.lat = lat
        self.lon = lon
        self.cfg = weather_cfg

    def fetch_current(self) -> dict:
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "current": "temperature_2m,precipitation,wind_speed_10m,weather_code",
            "timezone": "Asia/Ho_Chi_Minh",
        }
        r = requests.get(self.BASE, params=params, timeout=15)
        r.raise_for_status()
        return r.json().get("current", {})

    def travel_time_factor(self, current: dict | None = None) -> tuple[float, str]:
        if current is None:
            current = self.fetch_current()

        rain = float(current.get("precipitation") or 0)
        wind = float(current.get("wind_speed_10m") or 0)
        temp = current.get("temperature_2m")
        code = current.get("weather_code")

        factor = 1.0
        notes = []

        if rain >= self.cfg.get("heavy_rain_mm", 10):
            factor *= self.cfg.get("heavy_rain_factor", 1.35)
            notes.append(f"mưa lớn {rain:.1f}mm")
        elif rain >= self.cfg.get("rain_threshold_mm", 1):
            factor *= self.cfg.get("rain_factor", 1.15)
            notes.append(f"mưa {rain:.1f}mm")

        if wind >= self.cfg.get("wind_threshold_kmh", 30):
            factor *= self.cfg.get("wind_factor", 1.08)
            notes.append(f"gió {wind:.0f} km/h")

        summary = (
            f"T={temp}°C, mã thời tiết={code}, hệ số={factor:.2f}"
            + (f" ({', '.join(notes)})" if notes else " (thời tiết bình thường)")
        )
        return factor, summary
