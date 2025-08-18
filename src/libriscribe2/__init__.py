"""
LibriScribe - Modern book creation CLI with rich output and type safety.

This package provides a comprehensive book creation system with AI-powered
content generation, validation, and publishing capabilities.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    # This reads the version that Hatch placed in the package metadata during the build
    __version__ = version("libriscribe2")
except PackageNotFoundError:
    # Fallback for when the package is not installed
    __version__ = "0.0.0"
