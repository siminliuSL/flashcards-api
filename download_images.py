import os
from pexels_api_python import PexelsAPI
from PIL import Image
import requests
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def download_image(query: str, output_file: str):
    # Initialize Pexels API
    api = Pexels(os.getenv("PEXELS_API_KEY"))
    
    # Search for photos
    photos = api.search_photos(query, per_page=1)
    
    if photos and len(photos) > 0:
        # Get the first photo
        photo = photos[0]
        
        # Get the medium-sized image URL
        image_url = photo.src['medium']
        
        # Download the image
        response = requests.get(image_url)
        if response.status_code == 200:
            # Save the image
            image = Image.open(BytesIO(response.content))
            image.save(output_file, "JPEG", quality=85)
            print(f"Image saved to {output_file}")
        else:
            print(f"Error downloading image: {response.status_code}")
    else:
        print(f"No images found for query: {query}")

def main():
    # Create output directory if it doesn't exist
    output_dir = "images"
    os.makedirs(output_dir, exist_ok=True)

    # List of words to download images for
    words = [
        "coffee cup",
        "tea cup",
        "glass of milk",
        "glass of water",
        "glass of juice"
    ]

    # Download image for each word
    for word in words:
        output_file = os.path.join(output_dir, f"{word.split()[0]}.jpg")
        download_image(word, output_file)

if __name__ == "__main__":
    main() 