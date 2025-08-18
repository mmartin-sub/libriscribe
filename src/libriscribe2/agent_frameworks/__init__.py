"""
Agent Frameworks Package

This package contains implementations for different agent frameworks.
Currently supports:
- AutoGen: Microsoft's multi-agent framework
- Future: Other frameworks can be added here
"""

from .autogen import AutoGenAgentWrapper, AutoGenBestPractices, AutoGenService

__all__ = ["AutoGenAgentWrapper", "AutoGenBestPractices", "AutoGenService"]
