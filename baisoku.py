import subprocess


def fast_enc(src):
  cmd = f'ffmpeg -i {src} -y -af atempo=1.5 tmp/baisoku.mp3'
  subprocess.run(cmd, stdout=False, stderr=False)
