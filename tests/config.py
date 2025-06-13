r"""Configuration for the test suite of Cambiato."""

# Standard library
from pathlib import Path

# =============================================================================================
# Constants
# =============================================================================================

TEST_DIR = Path(__file__).parent
STATIC_FILES_BASE_DIR = TEST_DIR / 'static_files'
STATIC_FILES_CONFIG_BASE_DIR = STATIC_FILES_BASE_DIR / 'config'
