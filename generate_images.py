import os
from dotenv import load_dotenv
from supabase import create_client, Client
import requests
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize Supabase client with service role key
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
tenor_key = os.getenv("TENOR_API_KEY")

print(f"Connecting to Supabase at: {supabase_url}")
print(f"Tenor API Key present: {'Yes' if tenor_key else 'No'}")

supabase: Client = create_client(supabase_url, supabase_key)

def fetch_and_upload_gif(word: str, flashcard_id: str):
    """
    Fetch GIF from Tenor and upload to Supabase storage
    """
    try:
        if not tenor_key:
            print("Error: TENOR_API_KEY not found in environment variables")
            return False

        # Tenor API search
        search_url = f"https://tenor.googleapis.com/v2/search?q={word}&key={tenor_key}&limit=1&media_filter=gif"
        print(f"Searching Tenor for: {word}")
        response = requests.get(search_url)
        print(f"Tenor API response status: {response.status_code}")

        if response.status_code != 200:
            print(f"Tenor API error: {response.text}")
            return False

        data = response.json()
        if not data.get('results'):
            print(f"No GIFs found for: {word}")
            print(f"Full Tenor response: {data}")
            return False

        # Get GIF URL
        gif_url = data['results'][0]['media_formats']['gif']['url']
        print(f"Found GIF URL: {gif_url}")

        # Download GIF
        print(f"Downloading GIF from Tenor")
        img_response = requests.get(gif_url)
        print(f"GIF download status: {img_response.status_code}")

        if img_response.status_code != 200:
            print(f"Error downloading GIF: {img_response.text}")
            return False

        # Prepare GIF for upload
        img_bytes = BytesIO(img_response.content)
        filename = f"{flashcard_id}.gif"

        # Upload to Supabase storage
        print(f"Uploading {filename} to flashcard-images bucket")
        response = supabase.storage.from_("flashcard-images").upload(
            filename,
            img_bytes.read(),
            file_options={"content-type": "image/gif", "x-upsert": "true"}
        )

        # Get public URL
        image_url = supabase.storage.from_("flashcard-images").get_public_url(filename)
        print(f"Generated public URL: {image_url}")

        # Update flashcard table
        supabase.table('flashcards').update({
            'image_link': image_url
        }).eq('id', flashcard_id).execute()

        print(f"Successfully processed GIF for: {word}")
        return True

    except Exception as e:
        print(f"Error processing GIF for {word}: {str(e)}")
        return False

def main():
    try:
        # Test Supabase connection
        print("\nTesting Supabase connection...")
        try:
            response = supabase.table('flashcards').select("count").execute()
            print("Successfully connected to Supabase")
        except Exception as e:
            print(f"Error connecting to Supabase: {str(e)}")
            return

        # Get all flashcards
        print("\nFetching flashcards from Supabase...")
        try:
            response = supabase.table('flashcards').select("*").execute()
            
            if not response:
                print("Error: No response from Supabase")
                return
                
            if not response.data:
                print("Error: No data in response")
                print("Response:", response)
                return
                
            flashcards = response.data
            print(f"Found {len(flashcards)} flashcards")
            
        except Exception as e:
            print(f"Error fetching flashcards: {str(e)}")
            return
        
        # Process each flashcard
        success_count = 0
        error_count = 0
        
        for flashcard in flashcards:
            try:
                english_text = flashcard.get('name')
                flashcard_id = flashcard.get('id')
                
                if not english_text or not flashcard_id:
                    print(f"\nSkipping flashcard with missing data: {flashcard}")
                    error_count += 1
                    continue
                
                print(f"\nProcessing flashcard: {english_text} (ID: {flashcard_id})")
                if fetch_and_upload_gif(english_text, flashcard_id):
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
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main() 