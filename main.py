import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import random
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Choice(BaseModel):
    word: str
    imageUrl: str

class Word(BaseModel):
    id: int
    word: str
    audioUrl: str
    choices: List[Choice]
    correctIndex: int

# Sample words with environment variable URLs
words = [
    Word(
        id=1,
        word="咖啡",  # coffee
        audioUrl=f"{os.getenv('AUDIO_URL')}/coffee.mp3",
        choices=[
            Choice(word="coffee", imageUrl=f"{os.getenv('IMAGE_URL')}/coffee.jpg"),
            Choice(word="tea", imageUrl=f"{os.getenv('IMAGE_URL')}/tea.jpg"),
            Choice(word="milk", imageUrl=f"{os.getenv('IMAGE_URL')}/milk.jpg")
        ],
        correctIndex=0
    ),
    Word(
        id=2,
        word="茶",  # tea
        audioUrl=f"{os.getenv('AUDIO_URL')}/tea-zh.mp3",
        choices=[
            Choice(word="milk", imageUrl=f"{os.getenv('IMAGE_URL')}/milk.jpg"),
            Choice(word="tea", imageUrl=f"{os.getenv('IMAGE_URL')}/tea.jpg"),
            Choice(word="coffee", imageUrl=f"{os.getenv('IMAGE_URL')}/coffee.jpg")
        ],
        correctIndex=1
    )
]

@app.get("/api/v1/words/random")
async def get_random_word():
    logger.info("Getting random word")
    word = random.choice(words)
    logger.info(f"Selected word: {word.word}")
    logger.info(f"Audio URL: {word.audioUrl}")
    return word

@app.post("/api/v1/words/check/{word_id}/{choice_index}")
async def check_word(word_id: int, choice_index: int):
    logger.info(f"Checking word {word_id} with choice {choice_index}")
    word = next((w for w in words if w.id == word_id), None)
    if not word:
        logger.error(f"Word {word_id} not found")
        raise HTTPException(status_code=404, detail="Word not found")
    
    is_correct = choice_index == word.correctIndex
    logger.info(f"Word {word.word} check result: {'correct' if is_correct else 'incorrect'}")
    return {"correct": is_correct}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 