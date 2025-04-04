import whisper # type: ignore
import datetime

from Transcription_Test import Transcribe

# Convertit un nombre de secondes en format timestamp SRT : HH:MM:SS,ms.
def seconds_to_timestamp(seconds):
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

# Charger le modèle Whisper
model = whisper.load_model("turbo")

transcriber = Transcribe(model=model, language="fr")

# Transcrire l'audio avec Whisper
result = transcriber.transcribe_audio(audio_file="ffmpeg-7.1.1/output_audio.wav")

# Afficher le dictionnaire pour voir ce que peut donner comme information le modèle
print(result)

# Créer un fichier SRT à partir des segments
with open("output_subtitles.srt", "w", encoding="utf-8") as srt_file:
    for i, segment in enumerate(result["segments"], start=1):
        if not segment["text"].startswith(" Sous-titrage"):
            start_timestamp = seconds_to_timestamp(segment["start"])
            end_timestamp = seconds_to_timestamp(segment["end"])
            text = segment["text"].strip()
            srt_file.write(f"{i}\n")
            srt_file.write(f"{start_timestamp} --> {end_timestamp}\n")
            srt_file.write(f"{text}\n\n")

print("Fichier SRT généré : output_subtitles.srt")
