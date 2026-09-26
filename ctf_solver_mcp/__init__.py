"""
CTF Solver MCP Server
Automatically solves CTF challenges through fragmentation and analysis
"""

__version__ = "0.1.0"
__author__ = "CTF Solver Team"

from .server import CTFSolver, app

__all__ = ["CTFSolver", "app"]
