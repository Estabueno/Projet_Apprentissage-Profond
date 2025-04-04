# Projet de Sous-titrage et Traduction Automatique de Vidéos

Ce projet a été développé dans le cadre du cours d'apprentissage profond **8INF887**. Il vise à automatiser le processus de sous-titrage et de traduction de vidéos en utilisant des techniques d'intelligence artificielle.

Pour l'utilisation de ffmpeg entrez la commande ci-joint dans le terminal : ffmpeg -i Test video.mp4 -vn -acodec pcm s16le -ar 16000 -ac 1 output audio.wav Ffmpeg-i Test video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 output audio.wav 

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

Téléchargez et installez ImageMagick depuis le site officiel. Assurez-vous d'ajouter ImageMagick à votre PATH ou de configurer MoviePy pour pointer vers l'exécutable.

### Sur Linux

Utilisez votre gestionnaire de paquets. Par exemple, sur Ubuntu :

```bash
sudo apt-get install imagemagick
```

## Configuration de MoviePy

Si MoviePy ne parvient pas à trouver ImageMagick, définissez la variable d'environnement `IMAGEMAGICK_BINARY` dans votre script Python. Par exemple, ajoutez au début de votre script :

```python
import os
os.environ["IMAGEMAGICK_BINARY"] = "/usr/local/bin/convert" 
```

## Dépannage

Si vous rencontrez l'erreur suivante :

```
OSError: MoviePy Error: creation of None failed because of the following error: [Errno 2] No such file or directory: 'unset'.
```

Cela signifie généralement qu'ImageMagick n'est pas installé ou que MoviePy ne parvient pas à localiser l'exécutable. Pour résoudre ce problème :

1. **Vérifiez l'installation d'ImageMagick** en suivant les instructions ci-dessus.
2. **Configurez la variable d'environnement** `IMAGEMAGICK_BINARY` dans votre script pour pointer vers le chemin correct de l'exécutable (par exemple `/usr/local/bin/convert`).