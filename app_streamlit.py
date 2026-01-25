import streamlit as st
import whisper
import os

st.set_page_config(page_title="Lecture Voice-to-Notes", layout="centered")

st.title("🎙️ Lecture Voice-to-Notes Generator")
st.write("Upload a lecture audio file and get instant notes")

model = whisper.load_model("base")

audio_file = st.file_uploader(
    "Upload Lecture Audio",
    type=["mp3", "wav", "m4a"]
)

if audio_file is not None:
    with open("temp_audio.mp3", "wb") as f:
        f.write(audio_file.read())

    st.info("Transcribing audio... Please wait ⏳")

    result = model.transcribe("temp_audio.mp3")

    st.success("Transcription Complete ✅")
    st.text_area("Transcribed Text", result["text"], height=300)

    os.remove("temp_audio.mp3")
