from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile

def speak(text):
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(fp.name + ".mp3")
        audio = AudioSegment.from_mp3(fp.name + ".mp3")
        play(audio)
