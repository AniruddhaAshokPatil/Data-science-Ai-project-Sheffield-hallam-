import logging

from src.api.config import cfg


def configure_logging() -> logging.Logger:
    # I centralize logging setup here so every API module reports with the
    # same format and severity level once the app is deployed.
    logger = logging.getLogger("fraud-api")
    logger.setLevel(getattr(logging, cfg.log_level, logging.INFO))
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(getattr(logging, cfg.log_level, logging.INFO))
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# I create one shared logger here so all API files can report useful messages
# in a consistent format while I run and debug the backend.
logger = configure_logging()
