import sys
import os
from pathlib import Path

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    Ensures compatibility with PyTMX by returning a string path.
    """
    try:
        # When running as exe (PyInstaller)
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # When running in development
        base_path = Path(__file__).parent.parent
    
    # Convert Windows backslashes to forward slashes for cross-platform compatibility
    relative_path = relative_path.replace('\\', '/')
    
    # Return as string rather than Path object for maximum compatibility
    return str(base_path / relative_path)