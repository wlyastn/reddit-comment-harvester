"""
Configuration utilities (kept for backwards compatibility).
Legacy module - no longer needed for basic scraping.
"""

from __future__ import annotations

from dataclasses import dataclass


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class ZoneConfig:
    """Deprecated: ZoneConfig is no longer used."""

    zone: str
    token: str

