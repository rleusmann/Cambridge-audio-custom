"""Constants for the Cambridge Audio integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final

DOMAIN: Final = "cambridge_audio"

ATTR_UNIT_ID: Final = "unit_id"

LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=30)

# Attributes

# Services
