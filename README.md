# YouTube Transcript API (FastAPI)

This project is a **FastAPI-based API** that extracts transcripts from YouTube videos using their video IDs. It is designed for professional-grade usage with clean separation between **service logic** and **HTTP handling**, providing **structured JSON responses** and proper **HTTP status codes**. The API generates both **SRT-style transcripts** and **cleaned text**, suitable for applications like blogging, subtitles, text analysis, or NLP workflows.

The API also includes **Swagger/OpenAPI documentation** with fully documented success and error responses, making it easy for developers to integrate.

## Features
- Fetch YouTube video transcripts by **video ID**
- Supports multiple languages (when available)
- Returns **cleaned transcript text** and **SRT-formatted transcript**
- Provides **structured JSON responses** with:
  - `status`: success or error
  - `code`: HTTP status code
  - `message`: descriptive message
  - `data` or `error`: transcript data or error details
- Custom exception handling with meaningful HTTP codes:
  - **200** → Success
  - **403** → Video private or transcript disabled
  - **404** → Video unavailable or deleted
  - **422** → Language not supported
  - **500** → Internal server error
- Dockerized with `Dockerfile` and `docker-compose` for easy deployment
- Swagger/OpenAPI documentation at `/docs` showing **all possible response codes with models**

---

## Project Structure

```
fastapi-transcripts/
│── app/
│   ├── **init**.py
│   ├── main.py
│   ├── routes.py
│   ├── services.py
│   ├── utils.py
│   ├── exceptions.py
│   └── schemas.py
│── requirements.txt
│── Dockerfile
│── docker-compose.yml
````

## Installation

1. Clone the repository:

```bash
git clone https://www.github.com/eidankhan/fastapi-yt-transcript-extractor.git
cd fastapi-yt-transcript-extractor
````

2. Build and run using Docker Compose:

```bash
docker-compose up --build
```

3. Access the API at: `http://localhost:8000`

4. Access Swagger docs at: `http://localhost:8000/docs`

## API Endpoints

### Health Check

```
GET /healthz
```

**Response:**

```json
{
  "status": "ok"
}
```

### Fetch Transcript

```
GET /transcripts/{video_id}?language={language_code}
```


Optional query parameter:

- `language` (string): Fetch transcript in a specific language, e.g., `en`, `es`. If not provided, defaults to the primary transcript language.

**Success Response (200):**

```json
{
  "status": "success",
  "code": 200,
  "data": {
    "video_id": "abcd1234",
    "language": "en",
    "language_code": "en",
    "transcript_cleaned": "Hello world...",
    "transcript_with_timestamps": "1\n00:00:00,000 --> 00:00:02,000\nHello\n..."
  }
}
```

**Error Responses:**

**403 – Video private or transcript disabled**

```json
{
  "status": "error",
  "code": 403,
  "message": "Video is private or transcript disabled",
  "error": "TranscriptsDisabled: Transcript not available"
}
```

**404 – Video unavailable**

```json
{
  "status": "error",
  "code": 404,
  "message": "Video unavailable",
  "error": "VideoUnavailable: The video is private or deleted"
}
```

**422 – Language not supported**

```json
{
  "status": "error",
  "code": 422,
  "message": "Language not supported",
  "error": "NoTranscriptFound: Transcript not available in requested language"
}
```

**500 – Internal server error**

```json
{
  "status": "error",
  "code": 500,
  "message": "Transcript extraction failed",
  "error": "Some unexpected internal error message"
}
```

Perfect! Here’s an **updated README.md snippet** that documents your logging setup professionally. You can merge it into your existing README under a new section, e.g., **Logging**.

## Logging

This API includes a **robust logging system** for monitoring, debugging, and auditing purposes.

### Features:
* **Console logs:** Real-time log messages appear in the terminal when running the API.
* **File logs:** Logs are saved to `logs/api.log` with rotation (max 5MB per file, 5 backups).
* **Automatic directory creation:** The `logs/` directory is automatically created at the project root if it does not exist.
* **Informative messages:**

  * **Routes:** Log incoming requests and response status.
  * **Services:** Log transcript fetching, errors, and processing steps.
  * **Utilities:** Log timestamp formatting and transcript cleaning progress.

### Docker Setup

When running with Docker, the logs directory is mounted to your host machine so you can access logs outside the container:

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
```

* `./logs` → Local folder on your host machine
* `/app/logs` → Folder inside the container where logs are written

### Accessing Logs

* **Console:** All log messages appear in real time during API execution.
* **Log file:** `logs/api.log` stores historical logs, including info and error messages.

The log file will automatically rotate when it reaches 5MB, keeping the last 5 files as backup.

## Technologies Used

* **Python 3.11**
* **FastAPI**
* **youtube-transcript-api**
* **Docker & Docker Compose**
* **Pydantic** for request/response validation
* **Uvicorn** as ASGI server