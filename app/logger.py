import os
import logging
from logging.handlers import RotatingFileHandler

# Determine project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logs directory path
logs_dir = os.path.join(project_root, "logs")
os.makedirs(logs_dir, exist_ok=True)  # Create directory if missing

# Full path to log file
log_file_path = os.path.join(logs_dir, "api.log")

# Create logger
logger = logging.getLogger("yt_transcript_api")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File handler with rotation
file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers once
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

logger.info(f"Logger initialized. Log file: {log_file_path}")
