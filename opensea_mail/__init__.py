"""Top-level package for the NFT and token price tracker."""

import logging
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent
CONFIG_PATH = BASE_PATH / "config"

logger = logging.getLogger("opensea_mail")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False
