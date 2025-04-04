from transformers import pipeline
import nltk # type: ignore

# Télécharger le tokenizer NLTK
nltk.download('punkt_tab')

# Créer le pipeline de traduction du français vers l'anglais
translator = pipeline("translation_fr_to_en", model="Helsinki-NLP/opus-mt-fr-en")

# Lire la transcription
with open("output_transcription.txt", "r", encoding="utf-8") as f:
    transcription_text = f.read()

# Segmenter le texte en phrases car les timestamps ne sont pas forcément représentative d'une phrase entière
sentences = nltk.tokenize.sent_tokenize(transcription_text, language="french")

# Traduire chaque phrase
translated_sentences = []
for sentence in sentences:
    translated = translator(sentence, max_length=512)
    translated_sentences.append(translated[0]['translation_text'])

# Combiner les phrases traduites en un texte complet
translated_text = "\n".join(translated_sentences)

# Ecrire le résultat dans un fichier
with open("output_translated.txt", "w", encoding="utf-8") as f:
    f.write(translated_text)

print("La traduction a été effectuée et enregistrée dans 'output_translated.txt'.")
