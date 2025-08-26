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

---
> # Token Limit & Rate Limiting

## 🛡️ In-Memory Rate Limiting (Issue #15) 

**Purpose:**  
Introduce basic rate limiting for the API to prevent abuse and enforce usage limits per user/API key.

### 🔹 Key Points

- **Per-user/API key limits:**  
  Each user must provide an `x-api-key` header. Requests without it are rejected (`401 Unauthorized`).  

- **Request limits:**  
  - Configurable `max_per_window` (e.g., 3 requests)  
  - Configurable `window_seconds` (e.g., 60 seconds)  

- **Enforcement:**  
  - Requests exceeding the limit return `429 Too Many Requests`  
  - Middleware attaches headers to all responses:  
    ```
    X-RateLimit-Limit      # Maximum requests allowed per window
    X-RateLimit-Remaining  # Remaining requests in current window
    X-RateLimit-Reset      # Timestamp when current window resets
    Retry-After            # Included on 429 responses
    ```

- **Implementation:**  
  - `app/limiting/memory.py` → in-memory counter per API key  
  - `app/limiting/deps.py` → FastAPI dependency for rate limiting  
  - `app/main.py` → middleware to attach headers  
  - `app/routes.py` → transcript endpoint protected via dependency  

- **Behavior:**  
  - 1st–`max_per_window` requests → `200 OK`  
  - Requests beyond limit → `429`  
  - No API key → `401 Unauthorized`  
  - Counters reset after the configured window period  

- **Limitations:**  
  - In-memory only → counters reset if the server restarts  
  - Suitable as an MVP / proof-of-concept before moving to persistent storage (Redis/Postgres)  

### 🔹 Example Requests

**Successful Request:**
```http
GET /api/transcripts?video_url=<id>
Headers: x-api-key: test-key

200 OK
{
  "transcript": "..."
}
````

**Rate Limit Exceeded:**

```http
GET /api/transcripts?video_url=<id>
Headers: x-api-key: test-key

429 Too Many Requests
{
  "detail": "Rate limit exceeded. Try again in 45 seconds."
}
```
## 🛡️ Persistent Rate Limiting (Issue #16)

Enhance the API with persistent rate limiting using Redis to ensure limits survive server restarts and support longer time windows (daily/monthly). This is crucial for preventing abuse and enabling monetization tiers.

### 🔹 Key Points

- **Persistence:**  
  - API usage per user/API key is stored in Redis.  
  - Counters survive **server restarts**.  

- **Limits & Windows:**  
  - Configurable `limit` (e.g., 100 requests per day for free users).  
  - Configurable `period_seconds` (daily = 86400s, monthly = 2592000s).  
  - Each user/API key gets a separate counter with an automatic expiration.

- **API Key Enforcement:**  
  - Requests must include `x-api-key` header.  
  - Missing API key → `401 Unauthorized`.  

- **Enforcement Behavior:**  
  - Allowed requests → `200 OK`  
  - Exceeding the limit → `429 Too Many Requests`  
  - Response headers provide usage information:

```

X-RateLimit-Limit      # Maximum requests per window
X-RateLimit-Remaining  # Remaining requests in current window
X-RateLimit-Reset      # Timestamp when current window resets
Retry-After            # Included in 429 responses

````

- **Integration with FastAPI:**  
  - Dependency function `redis_rate_limit_dependency` returns an async function `_dep`.  
  - Applied per route using `Depends(redis_rate_limit_dependency)`.  
  - Handles attaching headers and raising HTTP exceptions automatically.  

- **Implementation:**  
  - `app/limiting/redis_client.py` → Redis connection setup.  
  - `app/limiting/persistent.py` → RedisLimiter class for counting requests.  
  - `app/limiting/deps.py` → FastAPI dependency for Redis rate limiting.  

- **Advantages over In-Memory Limiter:**  
  - Limits persist across restarts.  
  - Supports longer periods (daily/monthly).  
  - Can be extended to **tiered plans** (free/paid/enterprise).  

---

### 🔹 Example Request/Response

**Successful Request:**
```http
GET /api/transcripts?video_url=<id>
Headers: x-api-key: test-key

200 OK
{
  "transcript": "..."
}
````

**Rate Limit Exceeded:**

```http
GET /api/transcripts?video_url=<id>
Headers: x-api-key: test-key

429 Too Many Requests
{
  "detail": "Rate limit exceeded. Try again in 43200 seconds."
}
```

### 🛡️ Token Bucket Limiter (Issue #17)

This strategy provides a more flexible rate-limiting model:

- Each user starts with a fixed number of tokens (e.g., `100/day`).
- Every API call consumes **1 token**.
- The bucket automatically refills at the beginning of each period (e.g., daily).

#### How It Works
- A Redis key stores the current token count for each user:
```

bucket:{api\_key}:{period\_start}

````
- The key expires automatically (`ex = period_seconds`).
- If no tokens remain, the API responds with `429 Too Many Requests`.

#### Example Response When Bucket Is Empty
```json
{
"detail": "No tokens left. Bucket refills in 86321 seconds."
}
````
#### Usage

Protect an endpoint with the dependency:

```python
from fastapi import Depends
from .deps import token_bucket_dependency

@app.get("/transcript", dependencies=[Depends(token_bucket_dependency())])
async def get_transcript():
    return {"msg": "Transcript data"}
```

---

✅ This limiter is recommended when you want **fair daily quotas per user** while still allowing burst traffic up to the token limit.


## 🔑 Tier-Based Rate Limiting (Free vs Paid Users) (Issue #18)

We support **different API usage limits** for Free vs Paid tiers.  
Currently, API keys and their tiers are **hardcoded** into the code (no dynamic lookup yet).

---

### 🛠 How It Works (Current State)
1. **Hardcoded API Keys & Limits**
   - Example:
     ```python
     # Example config (not dynamic lookup yet)
     FREE_TIER_LIMIT = 100   # requests/day
     PAID_TIER_LIMIT = 1000  # requests/day
     ```
   - The system assigns these limits manually in the limiter setup.

2. **Rate Limiting**
   - Each limiter uses the configured max requests depending on the tier.
   - But right now, this is **wired manually in code** (not fetched by looking up the API key).

3. **Request Handling**
   - Clients must include `x-api-key` in headers.
   - Currently, the system **does not validate** whether the key is valid or which tier it belongs to.
   - The only difference is that **different hardcoded keys are associated with different rate limits in code**.

### ✅ Example

**Free Tier (hardcoded limit 100/day)**
```http
GET /api/resource
x-api-key: free-user-key
````

**Paid Tier (hardcoded limit 1000/day)**

```http
GET /api/resource
x-api-key: paid-user-key
```

## 🔑 API Key / Authentication Integration (Issue #19)

This API requires every request to include a valid `x-api-key` header. The system ensures:

1. Only registered users with valid API keys can access endpoints.
2. Requests exceeding the assigned tier limits are rejected.
3. Rate-limit headers are included in the response for client feedback.

---

### User Registration
- Users are registered via the `/register` endpoint.
- Each user receives a unique API key stored in the database.
- Example fields stored: `name`, `email`, `hashed password`, `api_key`, `tier`, `created_at`.

---

### Validating API Key
- All protected endpoints now check if the `x-api-key` exists in the database.
- Requests with:
  - Missing `x-api-key` → **401 Unauthorized**
  - Invalid `x-api-key` → **401 Unauthorized**
  - Valid `x-api-key` → proceeds to tier and rate-limit checks

---

### Tiered Token Bucket Strategy
- The system looks up the tier for the API key (Free / Paid / Custom).
- Each tier has configurable daily/monthly request limits.
- Token bucket algorithm:
  - Each user gets a bucket of tokens based on their tier.
  - Every API call consumes 1 token.
  - Bucket refills at the start of a new period.
- Requests exceeding the bucket → **429 Too Many Requests**

### Notes

* This ensures a **real-world, secure, and tiered access control** system.
* Future enhancements:

  * Dynamic tier configuration from admin panel.
  * Integration with external OAuth providers.

---

> # Performance Optimization

## Async Endpoints for Transcript Fetching (Issue #15) 

Convert the FastAPI transcript fetching endpoint to support asynchronous requests, enabling concurrent handling of multiple requests and reducing response time under load.

## Approach Implemented

1. **Async FastAPI Endpoint**
   * Converted the route to `async def fetch_transcript`.
   * Retained existing logging, error handling, and rate-limiting dependencies.

2. **Handling Synchronous Service**
   * `get_transcript()` from `youtube_transcript_api` is synchronous.
   * To prevent blocking the event loop, the synchronous function is executed in a **thread pool** using:
     ```python
     await loop.run_in_executor(executor, get_transcript, video_id, language)
     ```
   * Thread pool executor (`ThreadPoolExecutor`) allows multiple transcript fetches to run concurrently.

3. **Concurrency Achieved**
   * Multiple requests can be processed in parallel without blocking FastAPI's event loop.
   * Current configuration (`max_workers=20`) supports ~20 simultaneous transcript fetches.
   * Existing rate limiting (`tiered_token_bucket_dependency`) is preserved to ensure per-user request control.

## Benefits

* **Reduced Response Time** – Multiple transcript requests handled in parallel instead of sequentially.
* **Stable Async Behavior** – Event loop remains free while synchronous service executes in threads.
* **Safe and Compatible** – Service layer (`get_transcript()`) remains unchanged; no modifications needed to `youtube_transcript_api`.
* **Maintainable** – Easy to extend with caching or future async service updates.

## Limitations

* **Thread-bound concurrency** – Limited by `max_workers` in the thread pool.
* **Not fully async** – `youtube_transcript_api` is synchronous, so scaling beyond hundreds of concurrent requests may require a different async fetching approach.
* **Resource Usage** – High concurrency may increase memory usage due to threads.

## ♻️ Caching frequently requested transcripts #2

This caching strategy improves API performance by reducing repeated calls to the YouTube Transcript API. Redis is used as the caching layer, storing transcript data for 24 hours.

### Workflow

1. **Cache Key Construction**
   - Each transcript is cached based on:
     ```
     transcript:{video_id}:{language}
     ```
   - Example: `transcript:dQw4w9WgXcQ:en`

2. **Cache Lookup**
   - When a transcript request is received:
     - The service first queries Redis for the cache key.
     - If a cached transcript exists, it is returned immediately.
     - If not, the YouTube Transcript API is called to fetch the transcript.

3. **Fetching and Processing**
   - If the transcript is not in cache:
     - Fetch from YouTube API.
     - Format the transcript and generate timestamps.
     - Store the processed result in Redis with a TTL of 24 hours.

4. **Caching**
   - The transcript is serialized (JSON) and stored in Redis with an expiration of 24 hours.
   - This ensures that repeated requests within 24 hours do not hit the YouTube API, reducing latency and load.

### Data Stored in Cache

Each cache entry is stored in the following format:

```json
{
  "video_id": "<video_id>",
  "language": "<language_name>",
  "language_code": "<language_code>",
  "transcript": "<formatted_transcript_text>",
  "transcript_with_timestamps": "<srt_formatted_transcript>"
}
````

* `video_id`: YouTube video ID
* `language`: Display name of the language
* `language_code`: ISO code of the language
* `transcript`: Cleaned and formatted transcript text
* `transcript_with_timestamps`: Transcript in SRT-like format

## Cache Expiry

* Each transcript is stored with a TTL of **24 hours**.
* After 24 hours, the cache entry automatically expires to prevent stale data.

## Benefits

* **Reduced API Calls**: Frequently requested transcripts are served from Redis.
* **Faster Response**: Eliminates network latency for cached transcripts.
* **Scalable**: Minimal additional checks and simple key format ensures Redis performance is not degraded.
* **TTL-based Expiry**: Ensures data freshness without manual cache management.