"""
Configuration management for the OSR Order GUI.
"""

import json
import os
from typing import Dict, Any

from config.constants import CONFIG_FILE
from config.defaults import DEFAULT_ORDER_VALUES
from utils.exceptions import ConfigurationError


class Config:
    """Manages application configuration persistence and defaults."""

    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file

    def load(self) -> Dict[str, Any]:
        """Load configuration, merging with defaults for missing keys."""
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in DEFAULT_ORDER_VALUES.items():
                    if key not in config:
                        config[key] = value
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            return DEFAULT_ORDER_VALUES.copy()

    def save(self, config: Dict[str, Any]) -> None:
        """Save configuration to file with error handling."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")

    def resolve_osr(self, config: Dict[str, Any]) -> str:
        """Get the effective OSR ID from config or environment."""
        return config.get("osr_id", os.environ.get("OSR_ID", ""))
