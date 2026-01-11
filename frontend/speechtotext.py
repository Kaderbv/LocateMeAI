import streamlit as st
import speech_recognition as sr

def speechtotext():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening for your command...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        st.success(f"You said: {command}")
        return command.lower()
    except Exception:
        st.error("Could not understand audio")
        return None
