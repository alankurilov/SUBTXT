from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from schemas.caption import Caption
app = FastAPI()

load_dotenv()
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm", "video/x-msvideo"}
MAX_UPLOAD_BYTES = 500 * 1024 * 1024
ANALYSIS_PROMPT = """Analyze this video and identify parts that may be difficult, unclear, unfamiliar, or require additional context for a viewer.

For each relevant part, provide a short descriptive title, start and end timestamps in seconds, and a clear explanation of what the viewer may not understand. Do not explain every part of the video: only include moments where context meaningfully helps the viewer understand what is happening. Return the result as a list of captions."""
@app.get("/")
async def root():
    return {"message": "Service for analysing video"}

def analyse_uploaded_video(path: str):
    api_key = os.getenv('GOOGLE_AI_KEY')
    if not api_key:
        raise RuntimeError('GOOGLE_AI_KEY is not configured on the server.')
    client = genai.Client(api_key=api_key)
    uploaded_file = client.files.upload(file=path)
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[uploaded_file, ANALYSIS_PROMPT],
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=list[Caption]),
        )
        return response.parsed or []
    finally:
        try:
            client.files.delete(name=uploaded_file.name)
        except Exception:
            pass


@app.post('/analyse-video')
async def analyse_video(video: UploadFile = File(...)):
    """Receive a user-selected video and return its contextual captions."""
    if not video.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Choose a video file first.')
    if video.content_type and video.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail='Use an MP4, MOV, WebM, or AVI video.')

    import tempfile
    from pathlib import Path
    temp_path = ''
    total_bytes = 0
    try:
        with tempfile.NamedTemporaryFile(suffix=Path(video.filename).suffix or '.mp4', delete=False) as temporary_file:
            temp_path = temporary_file.name
            while chunk := await video.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail='Video must be 500 MB or smaller.')
                temporary_file.write(chunk)
        try:
            captions = await run_in_threadpool(analyse_uploaded_video, temp_path)
        except RuntimeError as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='Video analysis failed. Please try again.') from error
        return {'captions': captions}
    finally:
        await video.close()
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)
