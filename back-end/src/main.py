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
ANALYSIS_PROMPT = """
Identify moments in the video where a short contextual caption could help viewers follow the conversation.

A moment is a specific reference or concept — such as a person, event, institution, policy, acronym, phrase or cultural reference — that appears in the conversation.

Flag all the moments in the video when both are true

Understanding depends on it — the viewer needs that context to follow the speaker’s point.
It isn’t already explained — the video does not sufficiently explain it nearby.
Surface all moments that meet both criteria.

Keep separate mentions as separate moments.
Do not omit qualifying moments.
Do not add references or concepts that do not appear in the script.
Recommend a shortlist

From the full list, recommend the moments that are:

most important to understanding the speaker’s point
most valuable to explain for the target audience
Recommend roughly the top 30–40%, with a minimum of 4 and maximum of 10 where possible. If fewer than 4 moments qualify, recommend only those that do.

For each moment, return:

Spoken phrase — the exact words used in the video (e.g. “Bernie”, “AFL”)
Reference title — the full, recognisable name of the reference (e.g. “Bernie Sanders”, “American Football League”). 35 characters max; prioritise brevity.
Explanatory caption — the minimum context needed to understand the reference in this conversation. 130 characters max; prioritise brevity.
Recommended — Yes / No
Return moments in the order they appear in the script.

"""
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
