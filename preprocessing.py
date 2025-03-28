import re

def preprocess_subtitles(input_file, output_file):
    # Depuis un fichier .srt, ne conserve que le "text" et le nettoye tres basiquement.
    processed_lines = []

    # Regex pour les infos du .srt (timestamps)
    time_pattern = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3}\s-->\s\d{2}:\d{2}:\d{2},\d{3}$')

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip les lignes vides, les lignes index et le Regex (les timestamps)
            if (not line) or (line.isdigit()) or (time_pattern.match(line)):
                continue
            
            # (line == le texte "brute") a partir d'ici
            # On peut ensuite traiter le texte
            line = line.lower()                     # tout en minuscule
            line = re.sub(r'[^\w\s]', '', line)     # enlever la ponctuation
            line = line.strip()                     # enlever les espaces en trop

            if line:
                processed_lines.append(line)

    # Ecrit dans le fichier que l'on precise
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for processed_line in processed_lines:
            out_f.write(processed_line + '\n')


if __name__ == "__main__":
    input_srt_path = "exemple.srt"
    output_txt_path = "exemple_clean.txt"

    preprocess_subtitles(input_srt_path, output_txt_path)
    print(f"\nSaved to: {output_txt_path}")