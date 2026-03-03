"""
Pytest configuration for YatsurugiCapture tests
Automatically sets up Python path to find src modules
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
