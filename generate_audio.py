import os
from gtts import gTTS
from io import BytesIO
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client with service role key
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role key instead of regular key
)

def generate_and_upload_audio(text: str, filename: str):
    """
    Generate audio file and upload to Supabase storage
    :param text: Chinese text to convert to speech
    :param filename: Name of the file in storage bucket
    """
    try:
        print(f"Generating audio for text: {text}")
        # Create gTTS object with Chinese language
        tts = gTTS(text=text, lang='zh-cn')
        
        # Save to BytesIO object instead of file
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        print(f"Uploading {filename} to flashcard-audio bucket...")
        # Upload to Supabase storage
        response = supabase.storage.from_("flashcard-audio").upload(
            filename,
            audio_bytes.read(),
            file_options = {
            "content-type": "audio/mpeg",
            "x-upsert": "true"  # Changed from boolean to string
        }
        )
        
        print(f"Successfully uploaded audio file: {filename}")
        return True
    except Exception as e:
        print(f"Error generating/uploading audio for {text}: {str(e)}")
        return False

def main():
    try:
        # Get all flashcards from Supabase
        print("Fetching flashcards from Supabase...")
        response = supabase.table('flashcards').select("*").execute()
        
        if not response or not response.data:
            print("Error: No flashcards found in the database")
            return
            
        flashcards = response.data
        print(f"Found {len(flashcards)} flashcards")
        
        # Generate audio for each word
        success_count = 0
        error_count = 0
        
        for flashcard in flashcards:
            try:
                chinese_text = flashcard.get('translation')
                flashcard_id = flashcard.get('id')
                word = flashcard.get('name')
                
                if not chinese_text or not flashcard_id:
                    print(f"Skipping flashcard with missing data: {flashcard}")
                    error_count += 1
                    continue
                
                # Create filename using the flashcard ID
                filename = f"{flashcard_id}_{word}.mp3"
                
                # Generate and upload audio file
                if generate_and_upload_audio(chinese_text, filename):
                    # Get the public URL
                    audio_url = supabase.storage.from_("flashcard-audio").get_public_url(filename)
                    
                    # Update Supabase with the audio link
                    supabase.table('flashcards').update({
                        'audio_link': audio_url
                    }).eq('id', flashcard_id).execute()
                    
                    print(f"Updated audio link for flashcard {flashcard_id}")
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"Error processing flashcard: {str(e)}")
                error_count += 1
                continue
        
        # Print summary
        print("\nSummary:")
        print(f"Total flashcards processed: {len(flashcards)}")
        print(f"Successfully generated: {success_count}")
        print(f"Errors: {error_count}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()