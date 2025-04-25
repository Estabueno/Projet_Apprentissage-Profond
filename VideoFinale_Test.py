from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip
import os

os.environ["IMAGEMAGICK_BINARY"] = "/opt/homebrew/bin/convert"


# Définir une fonction qui génère un clip de texte pour chaque sous-titre
def subtitle_generator(txt):
    return TextClip(txt,font="Arial",fontsize=22, color="white")

# Charger la vidéo d'origine
video = VideoFileClip("ffmpeg-7.1.1/batman.mp4")

# Charger le fichier de sous-titres au format SRT et créer le clip de sous-titres
subtitles = SubtitlesClip("corrected.srt", subtitle_generator)

# Superposer les sous-titres sur la vidéo, positionnés en bas au centre
video_with_subs = CompositeVideoClip([video, subtitles.set_pos(('center', 'bottom'))])

# Sauvegarder la vidéo résultante
video_with_subs.write_videofile("video_with_subs.mp4", fps=video.fps)

