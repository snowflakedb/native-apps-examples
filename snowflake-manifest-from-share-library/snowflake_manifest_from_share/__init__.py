"""
Snowflake Manifest from Share

A Python library to create declarative application manifests from secure data shares.
"""

__version__ = "0.1.0"
__author__ = "Mohammed Shamil"

from .share_manifest_generator import ShareManifestGenerator
from .connection import SnowflakeConnection
from .yaml_formatter import YAMLFormatter

__all__ = ["ShareManifestGenerator", "SnowflakeConnection", "YAMLFormatter"]