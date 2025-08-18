"""
AutoGen Framework Implementation

This module provides AutoGen-specific implementations for libriscribe2.
"""

from .service import AutoGenConfigurationManager, AutoGenService
from .wrapper import AutoGenAgentWrapper, AutoGenBestPractices

__all__ = [
    "AutoGenAgentWrapper",
    "AutoGenBestPractices",
    "AutoGenConfigurationManager",
    "AutoGenService",
]
