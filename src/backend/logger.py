import logging

logger = logging.getLogger("fraud-mvp")
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler()
_handler.setLevel(logging.INFO)
_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
_handler.setFormatter(_formatter)

if not logger.handlers:
    logger.addHandler(_handler)