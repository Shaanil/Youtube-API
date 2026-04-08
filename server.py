import os
import subprocess

import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI()

def get_video_info(video_id):
    # Ensure no hidden characters or whitespace
    video_id = video_id.strip()
    full_url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'nocheckcertificate': True,
        'force_generic_extractor': False,
        'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(full_url, download=False)
            stream_url = info.get("url")
            if not stream_url:
                raise ValueError("No audio stream URL found")
            return {"stream_url": stream_url}
        except Exception as e:
            print(f"Extraction Error: {e}")
            raise RuntimeError("Failed to extract audio stream") from e


@app.get("/")
async def root():
    return JSONResponse(
        {
            "status": "ok",
            "service": "yt-mp3",
            "usage": "/stream/{video_id}",
        }
    )


@app.get("/health")
async def healthcheck():
    return {"status": "healthy"}


@app.get("/stream/{video_id}")
async def stream_endpoint(video_id: str):
    print(f"Streaming Video ID: {video_id}")
    try:
        video_data = get_video_info(video_id)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    def stream_audio():
        command = [
            'ffmpeg', '-i', video_data["stream_url"],
            '-f', 'mp3', '-acodec', 'libmp3lame', '-ab', '128k', '-vn',
            '-loglevel', 'error', 'pipe:1'
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            while True:
                chunk = process.stdout.read(4096)
                if not chunk: break
                yield chunk
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

    return StreamingResponse(stream_audio(), media_type="audio/mpeg")

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
