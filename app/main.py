from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic

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
def home():
    return {"message": "Backend is running"}

@app.get("/search")
def search(q: str = Query(..., min_length=1)):
    results = yt.search(q, filter="songs")

    cleaned_results = []
    for item in results[:10]:
        artists = item.get("artists", [])
        artist_name = artists[0]["name"] if artists else "Unknown Artist"

        thumbnails = item.get("thumbnails", [])
        artwork_url = thumbnails[-1]["url"] if thumbnails else ""

        cleaned_results.append({
            "id": item.get("videoId", ""),
            "title": item.get("title", "Unknown Title"),
            "artist": artist_name,
            "artworkURL": artwork_url
        })

    return cleaned_results