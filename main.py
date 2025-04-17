from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import random
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path to the assets directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Mount static files directory
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# Models
class Word(BaseModel):
    id: int
    word: str
    audioUrl: str
    images: List[str]
    correctIndex: int

class AnswerCheck(BaseModel):
    isCorrect: bool
    correctIndex: int

words = [
    {
        "id": 1,
        "word": "coffee",
        "audioUrl": "/assets/audio/coffee.mp3",
        "images": [
            "/assets/images/coffee.svg",
            "/assets/images/coffee.svg",
            "/assets/images/coffee.svg"
        ],
        "correctIndex": 0
    },
    {
        "id": 2,
        "word": "banana",
        "audioUrl": "https://upload.wikimedia.org/wikipedia/commons/3/3c/En-uk-banana.ogg",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/320px-Banana-Single.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Red_Apple.jpg/265px-Red_Apple.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Orange-Whole-%26-Split.jpg/320px-Orange-Whole-%26-Split.jpg"
        ],
        "correctIndex": 0
    },
    {
        "id": 3,
        "word": "orange",
        "audioUrl": "https://upload.wikimedia.org/wikipedia/commons/3/3c/En-uk-orange.ogg",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Orange-Whole-%26-Split.jpg/320px-Orange-Whole-%26-Split.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Red_Apple.jpg/265px-Red_Apple.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Banana-Single.jpg/320px-Banana-Single.jpg"
        ],
        "correctIndex": 0
    }
]

@app.get("/api/v1/words/random", response_model=Word)
async def get_random_word():
    return random.choice(words)

@app.post("/api/v1/words/check/{word_id}/{choice_index}", response_model=AnswerCheck)
async def check_answer(word_id: int, choice_index: int):
    word = next((w for w in words if w["id"] == word_id), None)
    if not word:
        return {"error": "Word not found"}
    
    is_correct = choice_index == word["correctIndex"]
    return {
        "isCorrect": is_correct,
        "correctIndex": word["correctIndex"]
    }

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    audio_path = os.path.join(ASSETS_DIR, "audio", filename)
    if not os.path.exists(audio_path):
        return {"error": "Audio file not found"}
    return FileResponse(audio_path, media_type="audio/mpeg")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 