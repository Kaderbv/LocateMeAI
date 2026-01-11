from gtts import gTTS
import pygame
import tempfile
import os

def speak(text):
    tts = gTTS(text)
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        temp_file = fp.name
    
    try:
        # Save audio to file
        tts.save(temp_file)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        # Clean up pygame
        pygame.mixer.quit()
    finally:
        # Delete temporary file
        if os.path.exists(temp_file):
            os.unlink(temp_file)
