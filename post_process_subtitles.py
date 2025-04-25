import re
from typing import List, Optional
import difflib
from transformers import pipeline

# Choix de comparaison avec un modèle de référence
REFERENCE_MODEL = True

# ----------------------------------------------------------------------
# Classe représentant une entrée SRT
# ----------------------------------------------------------------------
class SRTEntry:
    def __init__(self, index: int, time_code: str, text: str):
        self.index = index
        self.time_code = time_code
        self.text = text

    def __str__(self):
        # Retourne l’entrée au format SRT (une ligne vide à la fin)
        return f"{self.index}\n{self.time_code}\n{self.text}\n\n"

# ----------------------------------------------------------------------
# Fonctions utilitaires pour le format SRT
# ----------------------------------------------------------------------
def parse_srt(content: str) -> List[SRTEntry]:
    """
    Parse le contenu SRT en entrées individuelles.
    Nettoie le texte, sépare en blocs et crée des SRTEntry.
    """
    content = content.strip().replace('\r\n', '\n')
    blocks = re.split(r'\n\n+', content)
    entries = []
    for block in blocks:
        if not block.strip():
            continue
        lines = block.split('\n')
        if len(lines) < 3:
            continue
        try:
            index = int(lines[0])
            time_code = lines[1]
            text = '\n'.join(lines[2:]).strip()
            if text:
                entries.append(SRTEntry(index, time_code, text))
        except ValueError:
            continue
    return entries

def time_to_seconds(time_str: str) -> float:
    """Convertit un time code 'HH:MM:SS,mmm' en secondes."""
    hours, minutes, rest = time_str.split(':')
    seconds, millis = rest.split(',')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000

def seconds_to_timecode(seconds: float) -> str:
    """Convertit des secondes en time code 'HH:MM:SS,mmm'."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def split_timecode(time_code: str) -> tuple:
    """Sépare le time code complet en début et fin."""
    return time_code.split(" --> ")

def create_timecode(start: float, end: float) -> str:
    """Crée un time code à partir des valeurs de début et de fin en secondes."""
    return f"{seconds_to_timecode(start)} --> {seconds_to_timecode(end)}"

# ----------------------------------------------------------------------
# Fonctions pour la correction et le formatage du texte
# ----------------------------------------------------------------------
def fix_punctuation(text: str) -> str:
    """
    Corrige la ponctuation :
    - Ajoute un espace après la ponctuation s'il manque
    - Supprime les espaces avant la ponctuation
    - Convertit les majuscules après des virgules en minuscules
    """
    text = re.sub(r'([,.!?:;])([^\s\d])', r'\1 \2', text)  # espace après ponctuation
    text = re.sub(r'\s+([,.!?:;])', r'\1', text)            # suppression espace avant ponctuation
    text = re.sub(r'([,.!?:;])([^\s\d])', r'\1 \2', text) 
    text = re.sub(r',\s+([A-Z])', lambda m: f", {m.group(1).lower()}", text)
    return text

def format_text(text: str, max_chars_per_line: int = 42) -> str:
    """
    Format le texte pour :
        - Mettre en majuscule la première lettre de chaque phrase
        - Ajouter une ponctuation finale si nécessaire
        - Découper en lignes n'excédant pas max_chars_per_line
    """
    if text and text[0].isalpha():
        text = text[0].upper() + text[1:]

    # Découpage par ponctuation finale et remise en majuscules au début de chaque segment
    parts = []
    current = ""
    for char in text:
        current += char
        if char in '.!?':
            parts.append(current.strip())
            current = ""
    if current:
        parts.append(current.strip())
    text = " ".join(part[0].upper() + part[1:] if part and part[0].islower() else part for part in parts)

    if text and text[-1] not in '.!?':
        text += '.'

    text = re.sub(r',\s+([A-Z])', lambda m: f", {m.group(1).lower()}", text)

    # Découpage en lignes de longueur maximale
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if current_line:
            tentative = current_line + " " + word
        else:
            tentative = word
        if len(tentative) <= max_chars_per_line:
            current_line = tentative
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "\n".join(lines) if len(lines) > 1 else text

def split_entry_by_lines(entry: SRTEntry) -> List[SRTEntry]:
    """
    Si une entrée SRT contient plusieurs lignes de texte,
    répartit l'intervalle de temps uniformément pour chaque ligne.
    """
    start_str, end_str = split_timecode(entry.time_code)
    start_seconds = time_to_seconds(start_str)
    end_seconds = time_to_seconds(end_str)
    total_duration = end_seconds - start_seconds
    lines = [line.strip() for line in entry.text.split('\n') if line.strip()]
    if not lines:
        return [entry]
    interval = total_duration / len(lines)
    new_entries = []
    for i, line in enumerate(lines):
        new_start = start_seconds + i * interval
        new_end = start_seconds + (i + 1) * interval
        new_time_code = create_timecode(new_start, new_end)
        new_entries.append(SRTEntry(0, new_time_code, line))
    return new_entries

def process_srt_with_line_split(srt_content: str) -> str:
    """
    Scinde les entrées SRT multi-lignes en plusieurs entrées (avec répartition uniforme des time codes).
    """
    original_entries = parse_srt(srt_content)
    new_entries = []
    for entry in original_entries:
        if "\n" in entry.text:
            new_entries.extend(split_entry_by_lines(entry))
        else:
            new_entries.append(entry)
    for i, entry in enumerate(new_entries):
        entry.index = i + 1
    return "\n\n".join(str(entry) for entry in new_entries)

def merge_srt_files(reference_entries: List[SRTEntry], original_entries: List[SRTEntry]) -> List[SRTEntry]:
    """
    Fusionne deux fichiers SRT :
    - reference_entries : fichier avec le texte correct et les timestamps de référence
    - original_entries : fichier avec les timestamps à conserver

    Pour chaque entrée originale, on cherche la meilleure correspondance dans les entrées de référence.
    On garde le timestamp original et on remplace le texte par le texte de référence.
    Ensuite, on ajoute toutes les entrées de référence non appariées en utilisant leurs timestamps d'origine.
    """
    merged_entries: List[SRTEntry] = []
    processed_refs = set()

    # Apparier les entrées originales
    for orig_entry in original_entries:
        orig_text = orig_entry.text.lower().strip()
        best_match = None
        best_idx = -1
        best_ratio = 0.0

        for i, ref_entry in enumerate(reference_entries):
            if i in processed_refs:
                continue
            ref_text = ref_entry.text.lower().strip()
            ratio = difflib.SequenceMatcher(None, orig_text, ref_text).ratio()
            if ratio > best_ratio and ratio > 0.6:
                best_ratio = ratio
                best_match = ref_entry
                best_idx = i

        if best_match:
            merged_entries.append(
                SRTEntry(
                    orig_entry.index,
                    orig_entry.time_code,
                    best_match.text
                )
            )
            processed_refs.add(best_idx)

    # Ajouter les références non appariées avec leur timestamp d'origine
    for i, ref_entry in enumerate(reference_entries):
        if i not in processed_refs:
            # On attribue un index provisoire (sera réindexé ensuite)
            merged_entries.append(
                SRTEntry(
                    0,
                    ref_entry.time_code,
                    ref_entry.text
                )
            )

    # Trier par heure de début
    merged_entries.sort(
        key=lambda e: time_to_seconds(split_timecode(e.time_code)[0])
    )

    # Réindexer en séquence
    for idx, entry in enumerate(merged_entries, start=1):
        entry.index = idx

    return merged_entries

# ----------------------------------------------------------------------
# Classe centrale de traitement SRT
# ----------------------------------------------------------------------
class SRTProcessor:
    def __init__(self, lang1: str = "fr", lang2: str = "en", max_chars: int = 42, split_lines: bool = True, reference_srt: Optional[str] = None):
        self.lang1 = lang1
        self.lang2 = lang2
        self.max_chars = max_chars
        self.split_lines = split_lines
        self.reference_entries = parse_srt(reference_srt) if reference_srt else None
        self.translator = None

        # Crée la pipeline de traduction une seule fois si la langue n'est pas le français
        model_name = f"Helsinki-NLP/opus-mt-{self.lang1}-{self.lang2}"
        print(f"Traduction '{self.lang1}' en '{self.lang2}'")
        self.translator = pipeline("translation", model=model_name)
    
    def process_entries(self, entries: List[SRTEntry]) -> List[SRTEntry]:
        # Fusionner avec référence si fournie
        if self.reference_entries:
            entries = merge_srt_files(self.reference_entries, entries)
        # Filtrer les entrées vides
        entries = [entry for entry in entries if entry.text.strip()]
        for entry in entries:
            # Traduction unique si un traducteur est configuré
            if self.translator:
                # On traduit et récupère le texte traduit
                result = self.translator(entry.text, max_length=512)
                entry.text = result[0]['translation_text']
            # Correction de la ponctuation et formatage
            entry.text = fix_punctuation(entry.text)
            entry.text = format_text(entry.text, self.max_chars)
            # Vérification finale pour les majuscules après virgule
            entry.text = re.sub(r',\s+([A-Z])', lambda m: f", {m.group(1).lower()}", entry.text)
        # Réindexer les entrées
        for i, entry in enumerate(entries):
            entry.index = i + 1
        return entries

    def process_srt(self, srt_content: str) -> str:
        entries = parse_srt(srt_content)
        entries = self.process_entries(entries)
        # Rassembler le contenu SRT
        result = "\n\n".join(str(entry) for entry in entries)
        # Diviser les entrées multi-lignes
        if self.split_lines:
            result = process_srt_with_line_split(result)
        # Nettoyage final : supprimer les blocs vides éventuels
        result = re.sub(r'\n\n+', '\n\n', result)
        return result

# ----------------------------------------------------------------------
# Fonction principale
# ----------------------------------------------------------------------
def main():
    # Demande de la langue de la vidéo
    lang1 = input("Entrez la langue parlée dans la vidéo (laisser vide pour 'fr') : ").strip() or "fr"
    # Demande de la langue à utiliser
    lang2 = input("Entrez la langue souhaitée (laisser vide pour 'en') : ").strip() or "en"

    # Lecture du fichier SRT d'entrée
    with open('output_subtitles_vosk.srt', 'r', encoding='utf-8') as f:
        original_srt = f.read()

    if REFERENCE_MODEL:
        # Lecture du SRT de référence
        with open('output_subtitles_whisper.srt', 'r', encoding='utf-8') as f:
            reference_srt = f.read()
    else:
        reference_srt = None

    # Création d'une instance du processeur SRT et traitement
    processor = SRTProcessor(lang1=lang1, lang2=lang2, max_chars=57, split_lines=True, reference_srt=reference_srt)
    corrected_srt = processor.process_srt(original_srt)

    # Sauvegarde du résultat dans un fichier
    with open('corrected.srt', 'w', encoding='utf-8') as f:
        f.write(corrected_srt)
    print("Traitement terminé, fichier 'corrected.srt' généré.")

if __name__ == "__main__":
    main()
