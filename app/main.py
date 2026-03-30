from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
import os

app = FastAPI()

yt = YTMusic()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Music backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "music-backend"
    }


@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    results = yt.search(q, filter="songs")

    cleaned_results = []

    for item in results[:10]:
        video_id = item.get("videoId") or ""

        artists = item.get("artists") or []
        artist_name = (
            artists[0].get("name", "Unknown Artist")
            if artists else "Unknown Artist"
        )

        thumbnails = item.get("thumbnails") or []
        artwork_url = (
            thumbnails[-1].get("url", "")
            if thumbnails else ""
        )

        cleaned_results.append({
            "id": video_id,
            "title": item.get("title") or "Unknown Title",
            "artist": artist_name,
            "artworkURL": artwork_url,
            "videoId": video_id
        })

    return cleaned_results
