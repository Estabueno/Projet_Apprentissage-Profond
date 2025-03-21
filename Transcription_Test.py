class Transcribe:
    """
    Classe permettant de transcrire un fichier audio en utilisant un modèle ASR.
    Le texte transcrit est formaté pour une meilleure lisibilité, et les lignes
    commençant par "Sous-titrage" sont exclues. Le résultat complet de la transcription
    est retourné et le texte filtré est sauvegardé dans un fichier.
    """
    def __init__(self, model, language: str, output_file: str = "output_transcription.txt"):
        """
        Initialise l'instance avec le modèle, la langue et le nom du fichier de sortie.
        
        Args:
            model: Le modèle ASR (par exemple, Whisper).
            language (str): La langue de transcription (ex: "fr" pour français).
            output_file (str, optional): Chemin vers le fichier où sauvegarder la transcription filtrée.
        """
        self.model = model
        self.language = language
        self.output_file = output_file

    def transcribe_audio(self, audio_file: str) -> dict:
        """
        Transcrit le fichier audio en spécifiant la langue.
        
        La méthode formate le texte en insérant un saut de ligne après chaque phrase,
        supprime les lignes commençant par "Sous-titrage" et sauvegarde le résultat dans un fichier.
        
        Args:
            audio_file (str): Chemin du fichier audio à transcrire.
        
        Returns:
            dict: Le résultat complet de la transcription, incluant le texte et les segments.
        """
        # Transcription de l'audio en spécifiant la langue
        result = self.model.transcribe(audio_file, language=self.language)
        
        # Ajouter un saut de ligne après chaque phrase pour avoir une meilleur lisibilité
        transcription_text = result["text"].replace(". ", ".\n")
        
        # Diviser le texte en lignes
        lines = transcription_text.split("\n")
        
        # Enlever les lignes avec "Sous-titrage"
        filtered_lines = [line for line in lines if not line.strip().startswith("Sous-titrage")]
        
        # Réassembler le texte filtré
        filtered_text = "\n".join(filtered_lines).strip()
        
        # Écriture du texte filtré dans le fichier de sortie
        with open(self.output_file, "w", encoding="utf-8") as txt_file:
            txt_file.write(filtered_text)
        
        return result
