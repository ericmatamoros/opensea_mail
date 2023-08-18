"""
Top-level package for Property Valuation tracker
"""
import os

from opensea_mail.logging import create_logger
from pathlib import Path


logger = create_logger(__name__)

BASE_PATH = Path(os.path.dirname(__file__))
CONFIG_PATH = BASE_PATH / "config"
DATA_PATH = BASE_PATH / "data"
