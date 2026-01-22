from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import subprocess
import whisper

app = Flask(__name__)

# Set uploads folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Set explicit FFmpeg path to avoid WinError 2
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\ffmpeg-2026-01-19-git-43dbc011fa-full_build\bin"

# Load Whisper model
model = whisper.load_model("base")  # you can change "base" to "small", "medium", etc.

# Allowed audio extensions
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a"}

def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

# Optional: convert any audio to WAV for Whisper
def convert_to_wav(input_path, output_path):
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path, output_path
    ], check=True)

@app.route("/", methods=["GET", "POST"])
def upload():
    transcript_text = ""
    if request.method == "POST":
        if "audio" not in request.files:
            return render_template("index.html", transcript="No file part")
        file = request.files["audio"]
        if file.filename == "":
            return render_template("index.html", transcript="No selected file")

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Check extension, convert if needed
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            # Auto-convert to WAV
            new_filename = os.path.splitext(filename)[0] + ".wav"
            new_filepath = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)
            convert_to_wav(filepath, new_filepath)
            filepath = new_filepath

        try:
            # Transcribe audio
            result = model.transcribe(filepath)
            transcript_text = result["text"]
        except Exception as e:
            transcript_text = f"Error: {str(e)}"

    return render_template("index.html", transcript=transcript_text)

if __name__ == "__main__":
    app.run(debug=True)
