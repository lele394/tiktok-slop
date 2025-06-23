# from tiktok_uploader.upload import upload_video
import config as cfg
# from tiktok_uploader.auth import AuthBackend

from tiktok_uploader.auth import AuthBackend
from tiktok_uploader.upload import upload_videos

auth = AuthBackend(cookies="cookies.txt")

# # single video
# upload_video(
#   path='./output_with_audio.mp4',
#   description=f"{cfg.TITLE} {cfg.BALLS[0]["name"]} or {cfg.BALLS[1]["name"]}? Follow to ask your question!",
#   cookies="cookies.txt", # directly passing cookies
#   backend=auth
# )


videos = [
  {
    'path': './output_with_audio.mp4',
    'description': f"{cfg.TITLE} {cfg.BALLS[0]["name"]} or {cfg.BALLS[1]["name"]}? Follow to ask your question!"
  }
]

upload_videos(videos=videos, auth=auth, browser="firefox")