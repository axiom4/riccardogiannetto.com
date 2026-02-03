"""
Image optimization utilities wrapper for standalone scripts.

This module handles path setup to make utils available outside rg_api.
"""
import os
import sys

# Add rg_api to path for standalone script execution
_RG_API_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rg_api')
if _RG_API_PATH not in sys.path:
    sys.path.insert(0, _RG_API_PATH)

# Re-export ImageOptimizer for convenience
try:
    from utils.image_optimizer import ImageOptimizer
    __all__ = ['ImageOptimizer']
except ImportError as e:
    raise ImportError(
        "Could not import ImageOptimizer. "
        "Make sure this script is run from the workspace root."
    ) from e
