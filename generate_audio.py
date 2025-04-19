import os
from google.cloud import texttospeech
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the client
client = texttospeech.TextToSpeechClient()

def generate_audio(text: str, output_file: str):
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code="cmn-CN",  # Mandarin Chinese
        name="cmn-CN-Wavenet-A",  # High-quality voice
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.8,  # Slightly slower for better clarity
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Write the response to the output file
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio content written to file '{output_file}'")

def main():
    # Create output directory if it doesn't exist
    output_dir = "audio"
    os.makedirs(output_dir, exist_ok=True)

    # List of Chinese words to generate audio for
    words = [
        "咖啡",  # coffee
        "茶",    # tea
        "牛奶",  # milk
        "水",    # water
        "果汁",  # juice
    ]

    # Generate audio for each word
    for word in words:
        output_file = os.path.join(output_dir, f"{word}.mp3")
        generate_audio(word, output_file)

if __name__ == "__main__":
    main() 