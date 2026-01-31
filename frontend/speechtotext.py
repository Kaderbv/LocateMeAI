import streamlit as st
import speech_recognition as sr
import io

def speechtotext(audio_bytes=None):
    """
    Convert speech to text using Google Speech Recognition.
    
    Args:
        audio_bytes: Audio bytes from Streamlit audio_input widget
        
    Returns:
        Transcribed text in lowercase or None if recognition fails
    """
    if audio_bytes is None:
        st.error("No audio provided")
        return None
        
    recognizer = sr.Recognizer()
    
    try:
        # Create AudioFile from bytes
        audio_file = sr.AudioFile(io.BytesIO(audio_bytes))
        
        with audio_file as source:
            audio_data = recognizer.record(source)
        
        # Recognize speech using Google Speech Recognition
        command = recognizer.recognize_google(audio_data)
        return command.lower()
        
    except sr.UnknownValueError:
        st.error("Could not understand audio")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        st.error(f"Error processing audio: {e}")
        return None
