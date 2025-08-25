import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from fastapi import APIRouter, Query, Depends, status
from fastapi.responses import JSONResponse

from app.services import get_transcript
from app.exceptions import TranscriptError
from app.schemas import SuccessResponse, ErrorResponse
from app.logger import logger
from app.limiting.deps import tiered_token_bucket_dependency

router = APIRouter(prefix="/v1/transcripts", tags=["transcripts"])

# Thread pool for running synchronous get_transcript without blocking event loop
executor = ThreadPoolExecutor(max_workers=20)  # adjust based on server resources

@router.get(
    "",
    response_model=SuccessResponse,
    responses={
        200: {"model": SuccessResponse, "description": "Transcript fetched successfully"},
        403: {"model": ErrorResponse, "description": "Video is private or transcript disabled"},
        404: {"model": ErrorResponse, "description": "Video unavailable"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Fetch transcript of a YouTube video",
    description="Returns cleaned transcript, raw data, and SRT-formatted timestamps.",
    dependencies=[Depends(tiered_token_bucket_dependency())],
)
async def fetch_transcript(
    video_id: str = Query(..., description="YouTube video ID, e.g., 'dQw4w9WgXcQ'"),
    language: Optional[str] = Query(None, description="Optional language code, e.g., 'en'")
):
    logger.info(f"Received request: video_id={video_id}, language={language}")
    loop = asyncio.get_event_loop()

    try:
        # Run the blocking get_transcript in a thread pool
        transcript = await loop.run_in_executor(executor, get_transcript, video_id, language)
        logger.info(f"Transcript fetched successfully for video_id={video_id}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=SuccessResponse(
                status="success",
                code=200,
                data=transcript,
            ).dict(),
        )

    except TranscriptError as e:
        logger.error(f"Error fetching transcript for video_id={video_id}: {e}")
        return JSONResponse(
            status_code=e.code,
            content=ErrorResponse(
                status="error",
                code=e.code,
                message=e.message,
                error=str(e),
            ).dict(),
        )
