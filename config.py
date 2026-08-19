#!/usr/bin/env python3
"""
Configuration loader
====================

Keeps deployment-specific values (serial number prefix, counter start,
printer name keywords, preferred COM ports) out of the source code.

Values are read from ``config.json`` next to this file. Any key that is
missing from the file falls back to the defaults below, so the application
still runs without a config file present.
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULTS = {
    # Prefix printed in front of the device serial number on the label.
    # Set to "" if your serial numbers already carry their own prefix.
    "serial_prefix": "",

    # Value the incremental tracking counter (STC) starts from.
    "counter_start": 60000,

    # Substrings matched (case-insensitive) against Windows printer names to
    # auto-select the label printer. Extend this for your own hardware.
    "printer_keywords": ["zebra", "gc420", "zdesigner", "thermal", "label"],

    # Optional second printer (e.g. a small board/PCB label printer).
    "secondary_printer_keywords": ["xprinter", "tsc", "pcb", "controller"],

    # COM ports tried in order before falling back to the first port found.
    "preferred_ports": ["COM7", "COM4", "COM3"],
    "baudrate": 115200,

    # Regex used to extract device fields from the incoming serial stream.
    "parse_pattern": r"##([A-Z0-9]+)\|([0-9]+)\|([0-9]+)\s*\|([0-9A-F]+)\|([A-F0-9:]+)##",
}


def load_config(path: str = CONFIG_FILE) -> dict:
    """Return the merged configuration (defaults overridden by config.json)."""
    config = dict(DEFAULTS)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            config.update(json.load(handle))
    except FileNotFoundError:
        logger.info("config.json not found, using built-in defaults")
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning(f"Could not read {path} ({exc}), using built-in defaults")
    return config


CONFIG = load_config()
