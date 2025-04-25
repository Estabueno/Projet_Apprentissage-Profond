import datetime
import json
import os
from vosk import Model, KaldiRecognizer, SetLogLevel
import wave
import sys
import subprocess

class VoskTranscribe:
    def __init__(self, model_path: str, language: str, output_file: str = "output_transcription.txt"):
        self.language = language
        self.output_file = output_file
        
        # Désactiver les logs non nécessaires
        SetLogLevel(-1)
        
        # Charger le modèle Vosk
        try:
            self.model = Model(model_path)
        except Exception as e:
            print(f"Erreur lors du chargement du modèle: {e}")
            print(f"Assurez-vous d'avoir téléchargé le modèle pour la langue {language} depuis https://alphacephei.com/vosk/models")
            sys.exit(1)

    def ensure_wav_format(self, audio_file: str) -> str:
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

    def transcribe_audio(self, audio_file: str) -> dict:
        # S'assurer que le fichier est au format WAV
        wav_file = self.ensure_wav_format(audio_file)
        
        # Ouvrir le fichier audio
        wf = wave.open(wav_file, "rb")
        
        # Préparer le reconnaisseur avec le modèle
        rec = KaldiRecognizer(self.model, wf.getframerate())
        rec.SetWords(True)  # Pour obtenir les timestamps par mot
        
        # Préparer les structures pour stocker les résultats
        results = []
        segments = []
        full_text = ""
        
        # Traiter l'audio par morceaux
        while True:
            data = wf.readframes(4000)  # Lire par blocs
            if len(data) == 0:
                break
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                results.append(result)
                
                if "result" in result:
                    segment_text = result.get("text", "")
                    if segment_text:
                        words = result.get("result", [])
                        if words:
                            start_time = words[0].get("start", 0)
                            end_time = words[-1].get("end", start_time)
                            
                            segment = {
                                "start": start_time,
                                "end": end_time,
                                "text": segment_text
                            }
                            segments.append(segment)
                            full_text += segment_text + " "
        
        # Récupérer le dernier résultat
        final_result = json.loads(rec.FinalResult())
        results.append(final_result)
        
        if "result" in final_result:
            segment_text = final_result.get("text", "")
            if segment_text:
                words = final_result.get("result", [])
                if words:
                    start_time = words[0].get("start", 0)
                    end_time = words[-1].get("end", start_time)
                    
                    segment = {
                        "start": start_time,
                        "end": end_time,
                        "text": segment_text
                    }
                    segments.append(segment)
                    full_text += segment_text + " "
        
        # Formater le texte pour une meilleure lisibilité
        formatted_text = full_text.replace(". ", ".\n").strip()
        
        # Diviser le texte en lignes
        lines = formatted_text.split("\n")
        
        # Enlever les lignes avec "Sous-titrage"
        filtered_lines = [line for line in lines if not line.strip().startswith("Sous-titrage")]
        
        # Réassembler le texte filtré
        filtered_text = "\n".join(filtered_lines).strip()
        
        # Écriture du texte filtré dans le fichier de sortie
        with open(self.output_file, "w", encoding="utf-8") as txt_file:
            txt_file.write(filtered_text)
        
        # Nettoyer le fichier temporaire si nécessaire
        if wav_file != audio_file:
            os.remove(wav_file)
        
        # Créer un résultat similaire à celui de Whisper pour la compatibilité
        return {
            "text": filtered_text,
            "segments": segments,
            "language": self.language
        }


# Convertit un nombre de secondes en format timestamp SRT : HH:MM:SS,ms.
def seconds_to_timestamp(seconds):
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def main():
    # Choix du modèle et de langue
    model_path = "vosk-model-en-us-0.42-gigaspeech"
    language = "en"
    
    if not os.path.exists(model_path):
        print(f"Le modèle Vosk pour {language} n'est pas trouvé.")
        print(f"Veuillez télécharger le modèle depuis https://alphacephei.com/vosk/models")
        print(f"et l'extraire dans un dossier nommé '{model_path}'")
        sys.exit(1)
    
    # Initialiser le transcripteur Vosk
    transcriber = VoskTranscribe(model_path=model_path, language=language)
    
    # Chemin du fichier audio à transcrire
    audio_file = "ffmpeg-7.1.1/batman_temp.wav"
    
    # Transcrire l'audio avec Vosk
    print(f"Transcription en cours de {audio_file}...")
    result = transcriber.transcribe_audio(audio_file=audio_file)
    
    print("Transcription terminée!")
    
    # Créer un fichier SRT à partir des segments
    with open("output_subtitles_vosk.srt", "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(result["segments"], start=1):
            if not segment["text"].startswith(" Sous-titrage"):
                start_timestamp = seconds_to_timestamp(segment["start"])
                end_timestamp = seconds_to_timestamp(segment["end"]+1.1)
                text = segment["text"].strip()
                srt_file.write(f"{i}\n")
                srt_file.write(f"{start_timestamp} --> {end_timestamp}\n")
                srt_file.write(f"{text}\n\n")
    
    print("Fichier SRT généré : output_subtitles_vosk.srt")


if __name__ == "__main__":
    main()