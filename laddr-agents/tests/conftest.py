"""
Test configuration and fixtures for Laddr agent tests.
"""
import pytest
import sys
from pathlib import Path

# Add the parent directory to path so we can import agents
sys.path.insert(0, str(Path(__file__).parent.parent))
