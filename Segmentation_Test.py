import whisper # type: ignore
import datetime
import sys
import subprocess
import os

from Transcription_Test import Transcribe

# Convertit un nombre de secondes en format timestamp SRT : HH:MM:SS,ms.
def seconds_to_timestamp(seconds):
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def ensure_wav_format(audio_file: str) -> str:
        # Vérifier si le fichier est déjà un WAV
        if audio_file.lower().endswith('.wav'):
            return audio_file
            
        # Sinon, convertir en WAV temporaire
        output_wav = os.path.splitext(audio_file)[0] + "_temp.wav"
        try:
            subprocess.run(
                ["ffmpeg", "-i", audio_file, "-ar", "16000", "-ac", "1", output_wav],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            return output_wav
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la conversion audio: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("FFmpeg n'est pas installé. Veuillez l'installer pour la conversion audio.")
            sys.exit(1)

# Charger le modèle Whisper
model = whisper.load_model("turbo")
audio_file = ensure_wav_format("ffmpeg-7.1.1/batman_temp.wav") # Chargement du fichier audio

transcriber = Transcribe(model=model, language="en")

# Transcrire l'audio avec Whisper
result = transcriber.transcribe_audio(audio_file=audio_file)

# Afficher le dictionnaire pour voir ce que peut donner comme information le modèle
print(result)

# Créer un fichier SRT à partir des segments
with open("output_subtitles_whisper.srt", "w", encoding="utf-8") as srt_file:
    for i, segment in enumerate(result["segments"], start=1):
        if not segment["text"].startswith(" Sous-titrage"):
            start_timestamp = seconds_to_timestamp(segment["start"])
            end_timestamp = seconds_to_timestamp(segment["end"]+1.1) # Ajout d'un délai pour les sous-titres
            text = segment["text"].strip()
            srt_file.write(f"{i}\n")
            srt_file.write(f"{start_timestamp} --> {end_timestamp}\n")
            srt_file.write(f"{text}\n\n")

print("Fichier SRT généré : output_subtitles_whisper.srt")
