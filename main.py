import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import random
import os
from dotenv import load_dotenv
from download_images import download_image
from gtts import gTTS
from pathlib import Path
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
os.makedirs("images", exist_ok=True)
app.mount("/images", StaticFiles(directory="images"), name="images")

# Mount static files directory for serving audio files
os.makedirs("assets/audio", exist_ok=True)
app.mount("/audio", StaticFiles(directory="assets/audio"), name="audio")

class Choice(BaseModel):
    image_link: str
    label: str
    translation: str

class WordQuestion(BaseModel):
    id: int
    word: str
    audio_link: str
    choices: List[Choice]
    correct_index: int

@app.get("/api/v1/words/random", response_model=WordQuestion)
def get_random_word():
    # Fetch all flashcards
    response = supabase.table('flashcards').select("*").execute()
    flashcards = response.data
    print("First flashcard:", flashcards[0])  # See all fields
    
    if not flashcards or len(flashcards) < 3:
        raise HTTPException(status_code=404, detail="Not enough flashcards in the database.")

    # Select a random word
    correct = random.choice(flashcards)
    print("Correct word:", correct)  # See all fields of correct word
    #print("Translation field:", correct.get('translation'))  # Specifically check translation
    
    # Select two distractors
    distractors = random.sample([f for f in flashcards if f['id'] != correct['id']], 2)
    #print("Distractor translations:", [d.get('translation') for d in distractors])  # Check distractor translations

    # Prepare choices and shuffle
    choices = [
        {
            "image_link": correct['image_link'],
            "label": correct['name'],
            "translation": correct['translation']
        },
        {
            "image_link": distractors[0]['image_link'],
            "label": distractors[0]['name'],
            "translation": distractors[0]['translation']
        },
        {
            "image_link": distractors[1]['image_link'],
            "label": distractors[1]['name'],
            "translation": distractors[1]['translation']
        }
    ]
    #print("Final choices:", choices)  # See what we're sending to frontend
    random.shuffle(choices)
    correct_index = choices.index(next(c for c in choices if c['image_link'] == correct['image_link']))

    return WordQuestion(
        id=correct['id'],
        word=correct['translation'],
        audio_link=correct['audio_link'],
        choices=[Choice(**c) for c in choices],
        correct_index=correct_index
    )

@app.post("/api/v1/words/check/{word_id}/{choice_index}/{correct_index}")
def check_word(word_id: int, choice_index: int, correct_index: int):
    # Compare the user's choice with the correct index
    is_correct = choice_index == correct_index
    
    print(f"Checking answer: choice_index={choice_index}, correct_index={correct_index}, is_correct={is_correct}")
    
    return {"correct": is_correct}

@app.post("/api/v1/images/generate")
async def generate_image(query: str):
    try:
        # Create a filename from the query
        filename = f"{query.lower().replace(' ', '_')}.jpg"
        output_file = os.path.join("images", filename)
        
        # Download the image
        download_image(query, output_file)
        
        # Return the URL of the generated image
        return {"imageUrl": f"/images/{filename}"}
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class AudioRequest(BaseModel):
    text: str

@app.post("/api/v1/audio/generate")
async def generate_audio(request: AudioRequest):
    try:
        # Create a filename from the text
        filename = f"{request.text[:10].replace(' ', '_')}.mp3"
        output_path = os.path.join("assets", "audio", filename)
        
        # Create gTTS object with Chinese language
        tts = gTTS(text=request.text, lang='zh-cn')
        
        # Save the audio file
        tts.save(output_path)
        
        audio_url = f"{os.getenv('AUDIO_URL')}/{filename}"
        return {"audioUrl": audio_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 