# Projet de Sous-titrage et Traduction Automatique de Vidéos

Ce projet a été développé dans le cadre du cours d'apprentissage profond **8INF887**. Il vise à automatiser le processus de sous-titrage et de traduction de vidéos en utilisant des techniques d'intelligence artificielle.

## Installation des modèles Vosk

Pour utiliser le script Vosk.py, vous devez télécharger les modèles de reconnaissance vocale correspondant aux langues parlées dans vos vidéos :

1. Visitez le [dépôt officiel des modèles Vosk](https://alphacephei.com/vosk/models)
2. Téléchargez les modèles pour les langues souhaitées (par exemple, `vosk-model-fr-0.22` pour le français, `vosk-model-en-us-0.22` pour l'anglais américain)
3. Décompressez les fichiers à la racine du projet
4. Dans le script Vosk.py, assurez-vous que le chemin vers le modèle correspond à votre structure de dossiers :

```python
# Exemple de configuration du modèle dans Vosk.py
model_path = "vosk-model-fr-0.22"  # Ajustez selon votre langue
```

Choisissez le modèle approprié en fonction de vos besoins et des ressources de votre système.

## Ordre d'exécution des scripts

Pour traiter une vidéo et générer les sous-titres traduits, suivez cette séquence d'exécution :

1. **Segmentation.py** - Segmente l'audio en fichier SRT avec Whisper Turbo
   ```bash
   python Segmentation.py
   ```

2. **Vosk.py** - Segmente l'audio een fichier SRT avec Vosk
   ```bash
   python Vosk.py
   ```

3. **post_process_subtitles.py** - Traite, optimise et traduis les sous-titres générés
   ```bash
   python post_process_subtitles.py
   ```

4. **VideoFinale_test.py** - Créer et intègre les sous-titres dans la vidéo finale
   ```bash
   python VideoFinale_test.py
   ```

Chaque script génère des fichiers intermédiaires qui seront utilisés par les scripts suivants dans la chaîne de traitement.

# MoviePy avec ImageMagick pour l'ajout de sous-titres

## Prérequis

* **ImageMagick** Utilisé pour la création des TextClips.

## Installation d'ImageMagick

### Sur macOS

Si vous utilisez Homebrew, installez ImageMagick avec :

```bash
brew install imagemagick
```

Vérifiez le chemin de l'exécutable `convert` avec :

```bash
which convert
```

Il se peut que le chemin soit, par exemple, `/opt/homebrew/bin/convert`.

### Sur Windows

1. Téléchargez et installez ImageMagick depuis le [site officiel](https://imagemagick.org/script/download.php#windows).
2. **Important** : Assurez-vous de cocher l'option "Install legacy utilities (e.g. convert)" lors de l'installation.
3. Assurez-vous d'ajouter ImageMagick à votre PATH système.
4. Dans votre script Python, configurez le chemin vers l'exécutable avec une syntaxe comme celle-ci :

```python
import os
# Pour Windows
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
```

Vous pouvez également utiliser la fonction `change_settings` de MoviePy :

```python
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})
```

## Configuration de MoviePy

### Sur macOS

Si MoviePy ne parvient pas à trouver ImageMagick, définissez la variable d'environnement `IMAGEMAGICK_BINARY` dans votre script Python :

```python
import os
os.environ["IMAGEMAGICK_BINARY"] = "/usr/local/bin/convert" 
```

### Sur Windows

Sur Windows, l'exécutable peut s'appeler `magick.exe` plutôt que `convert` dans les versions récentes :

```python
import os
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
```

## Dépannage

Si vous rencontrez l'erreur suivante :

```
OSError: MoviePy Error: creation of None failed because of the following error: [Errno 2] No such file or directory: 'unset'.
```

Cela signifie généralement qu'ImageMagick n'est pas installé ou que MoviePy ne parvient pas à localiser l'exécutable. Pour résoudre ce problème :

1. **Vérifiez l'installation d'ImageMagick** en suivant les instructions ci-dessus.
2. **Configurez la variable d'environnement** `IMAGEMAGICK_BINARY` dans votre script pour pointer vers le chemin correct de l'exécutable.
3. **Sur Windows**, vérifiez que le chemin est bien entouré de la notation `r"..."` pour éviter les problèmes avec les caractères d'échappement.
4. **Redémarrez** votre environnement de développement après avoir installé ImageMagick.
