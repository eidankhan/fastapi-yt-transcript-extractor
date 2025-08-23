from datetime import timedelta
import re
from app.logger import logger

def format_timestamp(seconds: float) -> str:
    """Converts seconds into SRT-style timestamp format."""
    logger.debug(f"Formatting timestamp for {seconds} seconds")
    ms = int((seconds - int(seconds)) * 1000)
    t = str(timedelta(seconds=int(seconds)))
    h, m, s = t.split(':')
    formatted_timestamp = f"{int(h):02}:{int(m):02}:{int(s):02},{ms:03}"
    logger.debug(f"Formatted timestamp: {formatted_timestamp}")
    return formatted_timestamp

def format_transcript(transcript) -> str:
    logger.info("Starting transcript formatting")
    raw_text = ' '.join(snippet.text for snippet in transcript.snippets)
    logger.debug(f"Raw transcript text length: {len(raw_text)} characters")

    # Remove all characters except letters, spaces, and punctuation
    cleaned_text = re.sub(r'[^a-zA-Z\s.!?]', '', raw_text)
    # Normalize whitespace
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    logger.info(f"Transcript formatting complete. Cleaned text length: {len(cleaned_text)} characters")
    return cleaned_text
