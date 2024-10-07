import requests
import os
CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/2gPFXx8pN3Avh27Dw5Ma"
# Code_ID_TAAL
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": "d9847431c85c7347a01d570a15784b3b"
}

responses = {
    "GRIPPER": {
        "EN": [
            "I'm exited."
        ]
    }
}

audio_dir = "audio"

for key, value in responses.items():
    for nested_key, sentences in value.items():
        for i, text in enumerate(sentences):
            if text:  # Skip empty strings
                data = {
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 1,
                        "similarity_boost": 1
                    }
                }

                response = requests.post(url, json=data, headers=headers)
                filename = f"goingBack2.mp3"
                # Voeg het pad naar de map toe aan de bestandsnaam
                filepath = os.path.join(audio_dir, filename)
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)