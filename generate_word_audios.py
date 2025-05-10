from gtts import gTTS
import os
from pathlib import Path
import json

def generate_audio_for_word(text: str, output_file: str):
    """
    Generate audio file from Chinese text
    :param text: Chinese text to convert to speech
    :param output_file: Output MP3 file path
    """
    try:
        # Create output directory if it doesn't exist
        Path(os.path.dirname(output_file)).mkdir(parents=True, exist_ok=True)
        
        # Create gTTS object with Chinese language
        tts = gTTS(text=text, lang='zh-cn')
        
        # Save the audio file
        tts.save(output_file)
        print(f"Generated audio file: {output_file}")
        return True
    except Exception as e:
        print(f"Error generating audio for {text}: {str(e)}")
        return False

def main():
    # Create output directory if it doesn't exist
    output_dir = "assets/audio"
    os.makedirs(output_dir, exist_ok=True)
    
    # Read words from words.json
    try:
        with open("assets/words.json", "r", encoding="utf-8") as f:
            words = json.load(f)
            
        # Generate audio for each word
        for word in words:
            chinese_text = word.get("word", "")
            if chinese_text:
                output_file = os.path.join(output_dir, f"{chinese_text}.mp3")
                generate_audio_for_word(chinese_text, output_file)
                print(f"Generated audio for: {chinese_text}")
            
    except FileNotFoundError:
        print("Error: assets/words.json file not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in words.json")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()