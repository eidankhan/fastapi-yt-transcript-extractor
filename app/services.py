from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import VideoUnavailable, TranscriptsDisabled, NoTranscriptFound

from app.utils import format_transcript, format_timestamp
from app.logger import logger
from app.exceptions import (
    VideoUnavailableError,
    VideoPrivateError,
    LanguageNotSupportedError,
    TranscriptFetchError,
)

def get_transcript(video_id: str, language: Optional[str] = None) -> dict:
    """
    Fetch transcript from YouTube, process it and return formatted data.
    This function is synchronous; it will be called in a thread pool for async endpoints.
    """
    logger.info(f"Fetching transcript for video_id={video_id}, language={language}")
    ytt_api = YouTubeTranscriptApi()

    try:
        if language:
            transcript = ytt_api.fetch(video_id, languages=[language])
        else:
            transcript = ytt_api.fetch(video_id)

    except VideoUnavailable:
        logger.info(f"Video unavailable or deleted for video_id={video_id}")
        raise VideoUnavailableError("Video unavailable or deleted")
    except TranscriptsDisabled:
        logger.info(f"Transcript disabled or video private for video_id={video_id}")
        raise VideoPrivateError("Transcript disabled or video private")
    except NoTranscriptFound:
        logger.info(f"Transcript not available in requested language for video_id={video_id}")
        raise LanguageNotSupportedError("Transcript not available in requested language")
    except Exception as e:
        logger.info(str(e))
        raise TranscriptFetchError(str(e))

    # Build transcript with timestamps
    lines = []
    for idx, snippet in enumerate(transcript.snippets, start=1):
        start_time = format_timestamp(snippet.start)
        end_time = format_timestamp(snippet.start + snippet.duration)
        lines.append(f"{idx}\n{start_time} --> {end_time}\n{snippet.text}\n")

    data = format_transcript(transcript)
    logger.info(f"Transcript processing complete for video_id={video_id}")

    return {
        "video_id": video_id,
        "language": transcript.language,
        "language_code": transcript.language_code,
        "transcript": data,
        "transcript_with_timestamps": "\n".join(lines),
    }
