import re
from typing import List, Dict, Tuple
import difflib
from transformers import pipeline

class SRTEntry:
    def __init__(self, index: int, time_code: str, text: str):
        self.index = index
        self.time_code = time_code
        self.text = text
    
    def __str__(self):
        # Ajouter une ligne vide supplémentaire à la fin de chaque entrée
        return f"{self.index}\n{self.time_code}\n{self.text}\n\n"

def parse_srt(content: str) -> List[SRTEntry]:
    """Parse le contenu SRT en entrées individuelles"""
    # Supprime les caractères invisibles et normalise les sauts de ligne
    content = content.strip().replace('\r\n', '\n')
    
    # Séparation des blocs
    blocks = re.split(r'\n\n+', content)
    entries = []
    
    for block in blocks:
        if not block.strip():  # Ignorer les blocs vides
            continue
            
        lines = block.split('\n')
        if len(lines) < 3:
            continue
        
        try:
            index = int(lines[0])
            time_code = lines[1]
            text = '\n'.join(lines[2:])
            
            # Ignorer les entrées dont le texte est vide
            if not text.strip():
                continue
                
            entries.append(SRTEntry(index, time_code, text))
        except ValueError:
            continue
    
    return entries

def format_text(text: str, max_chars_per_line: int = 42) -> str:
    """Formate le texte avec ponctuation et majuscules, sans majuscules après virgules"""
    # Mettre en majuscule au début du texte
    if text and text[0].isalpha():
        text = text[0].upper() + text[1:]
    
    # Mettre en majuscule après les ponctuations finales (sauf virgules)
    parts = []
    current = ""
    
    for char in text:
        current += char
        if char in '.!?':
            parts.append(current)
            current = ""
    
    if current:  # Ajouter la dernière partie si elle existe
        parts.append(current)
    
    # Mettre en majuscule le premier caractère de chaque partie (après un point)
    result = ""
    for part in parts:
        part = part.strip()
        if part and part[0].isalpha():
            part = part[0].upper() + part[1:]
        result += part + " "
    
    text = result.strip()
    
    # Ajout des points à la fin des phrases si nécessaire
    if text and not text.strip().endswith(('.', '!', '?', '...', ':', ',')):
        text += '.'
    
    # S'assurer explicitement qu'il n'y a pas de majuscule après une virgule
    text = re.sub(r',\s+([A-Z])', lambda m: f", {m.group(1).lower()}", text)
    
    # Format pour respecter le nombre maximum de caractères par ligne
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= max_chars_per_line or not current_line:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Si on a plus d'une ligne, on les formate correctement
    if len(lines) > 1:
        return '\n'.join(lines)
    return text

def fix_punctuation(text: str) -> str:
    """Corrige la ponctuation"""
    # Ajoute un espace après les virgules, points, etc. s'il n'y en a pas
    text = re.sub(r'([,.!?:;])([^\s\d])', r'\1 \2', text)
    
    # Supprime les espaces avant la ponctuation
    text = re.sub(r'\s+([,.!?:;])', r'\1', text)
    
    # Ajoute un espace après la ponctuation si nécessaire
    text = re.sub(r'([,.!?:;])([^\s\d])', r'\1 \2', text)
    
    # Assure qu'il n'y a JAMAIS de majuscule après une virgule
    text = re.sub(r',\s+([A-Z])', lambda m: f", {m.group(1).lower()}", text)
    
    return text

def compare_and_merge_srt(original_entries: List[SRTEntry], reference_entries: List[SRTEntry]) -> List[SRTEntry]:
    """Compare et fusionne deux fichiers SRT"""
    merged_entries = []
    
    # Créer un dictionnaire des textes de référence
    reference_texts = {entry.text.lower().strip(): entry for entry in reference_entries}
    
    for original in original_entries:
        best_match = None
        best_ratio = 0
        original_text_lower = original.text.lower().strip()
        
        # Chercher la meilleure correspondance dans les références
        for ref_text, ref_entry in reference_texts.items():
            ratio = difflib.SequenceMatcher(None, original_text_lower, ref_text).ratio()
            if ratio > best_ratio and ratio > 0.7:  # Seuil de correspondance à 70%
                best_ratio = ratio
                best_match = ref_entry
        
        # Créer une nouvelle entrée avec les meilleurs éléments
        new_entry = SRTEntry(original.index, original.time_code, original.text)
        
        if best_match:
            # Utiliser le texte de référence s'il semble meilleur (plus long ou plus formaté)
            if len(best_match.text) > len(original.text) or ',' in best_match.text or '.' in best_match.text:
                new_entry.text = best_match.text
                
                # S'assurer qu'il n'y a pas de majuscule après une virgule dans le texte de référence
                new_entry.text = re.sub(r',\s+([A-Z])', lambda m: f", {m.group(1).lower()}", new_entry.text)
        
        merged_entries.append(new_entry)
    
    return merged_entries

def time_to_seconds(time_str: str) -> float:
    """Convertit un time code 'HH:MM:SS,mmm' en secondes"""
    hours, minutes, rest = time_str.split(':')
    seconds, millis = rest.split(',')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000

def seconds_to_timecode(seconds: float) -> str:
    """Convertit des secondes en time code 'HH:MM:SS,mmm'"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def split_timecode(time_code: str) -> tuple:
    """Sépare le time code en début et fin"""
    return time_code.split(" --> ")

def create_timecode(start: float, end: float) -> str:
    """Crée un time code à partir des temps de début et de fin en secondes"""
    return f"{seconds_to_timecode(start)} --> {seconds_to_timecode(end)}"

def split_entry_by_lines(entry: SRTEntry) -> List[SRTEntry]:
    """
    Pour une entrée SRT avec plusieurs lignes de texte,
    répartit l'intervalle de temps en parts égales pour chaque ligne.
    """
    # Sépare le time code en début et fin
    start_str, end_str = split_timecode(entry.time_code)
    start_seconds = time_to_seconds(start_str)
    end_seconds = time_to_seconds(end_str)
    total_duration = end_seconds - start_seconds

    # Sépare le texte par sauts de ligne
    lines = entry.text.strip().split('\n')
    n = len(lines)
    if n == 0:
        return [entry]

    interval = total_duration / n
    new_entries = []
    for i, line in enumerate(lines):
        # Ignorer les lignes vides
        if not line.strip():
            continue
            
        new_start = start_seconds + i * interval
        new_end = start_seconds + (i + 1) * interval
        new_time_code = create_timecode(new_start, new_end)
        # On crée une nouvelle entrée avec le texte de la ligne
        new_entries.append(SRTEntry(0, new_time_code, line.strip()))
    return new_entries

def process_srt_with_line_split(srt_content: str) -> str:
    """Traite le fichier SRT en scindant les entrées multi-lignes en plusieurs time stamps"""
    original_entries = parse_srt(srt_content)
    new_entries = []
    for entry in original_entries:
        # Si l'entrée contient plusieurs lignes, on les sépare en plusieurs entrées
        if '\n' in entry.text:
            splitted = split_entry_by_lines(entry)
            new_entries.extend(splitted)
        else:
            new_entries.append(entry)

    # Réattribuer les index
    for i, entry in enumerate(new_entries):
        entry.index = i + 1
    
    # Regénérer le contenu SRT
    return '\n\n'.join(str(entry) for entry in new_entries)

def fix_srt(srt_content: str, reference_srt: str = None, max_chars: int = 42,lang = "fr", split_lines: bool = True) -> str:
    """Fonction principale pour corriger un fichier SRT"""
    import difflib

    entries = parse_srt(srt_content)
    
    # Si un SRT de référence est fourni, le comparer et fusionner
    if reference_srt:
        reference_entries = parse_srt(reference_srt)
        entries = compare_and_merge_srt(entries, reference_entries)
    
    # Filtrer les entrées vides
    entries = [entry for entry in entries if entry.text.strip()]

    if lang != "fr":
        translator = pipeline("translation_fr_to_other", model="Helsinki-NLP/opus-mt-fr-"+lang)
    
    # Corriger chaque entrée
    for entry in entries:
        if(lang != "fr"):
            entry.text = translator(entry.text,max_length=512)
        # Corriger la ponctuation (à faire avant le formatage)
        entry.text = fix_punctuation(entry.text)
        # Formater le texte
        entry.text = format_text(entry.text, max_chars)
        # Vérification finale pour les majuscules après virgules
        entry.text = re.sub(r',\s+([A-Z])', lambda m: f", {m.group(1).lower()}", entry.text)
    
    # Recalculer les index
    for i, entry in enumerate(entries):
        entry.index = i + 1
    
    # Générer le contenu SRT
    result = '\n\n'.join(str(entry) for entry in entries)
    
    # Si demandé, diviser les entrées multi-lignes
    if split_lines:
        result = process_srt_with_line_split(result)
        
    # Vérification finale pour s'assurer qu'il n'y a pas de blocs vides
    result = re.sub(r'\n\n+', '\n\n', result)
    
    return result

def main():
    # Charger vos fichiers SRT
    with open('output_subtitles_vosk.srt', 'r', encoding='utf-8') as f:
        original_srt = f.read()

    with open('output_subtitles.srt', 'r', encoding='utf-8') as f:
        reference_srt = f.read()


    # Corriger le SRT, avec ou sans division des lignes
    corrected_srt = fix_srt(original_srt, max_chars=55, split_lines=True,lang = "en")

    # Sauvegarder le résultat
    with open('corrected.srt', 'w', encoding='utf-8') as f:
        f.write(corrected_srt)

if __name__ == "__main__":
    main()