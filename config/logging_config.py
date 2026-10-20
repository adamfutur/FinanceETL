import sys
from loguru import logger
from config.settings import settings

def setup_logging():
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file handler
    logger.add(
        "logs/etl_{time}.log",
        rotation="10 MB",
        retention="1 month",
        level="DEBUG",
        compression="zip"
    )
    
    logger.info("Logging setup complete.")

setup_logging()
