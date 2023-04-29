import glob
import os
import re
import subprocess
from discord.player import FFmpegPCMAudio
import pydub
import asyncio

from config.config import *
import baisoku

# Do not output log when message is encoded
import logging
logging.getLogger("discord.player").setLevel(logging.ERROR)
logging.getLogger("discord.voice_client").setLevel(logging.ERROR)


msg = []
i = 0
count = 0



async def fast(text, message, voiceChannel, client):
  global i, count
  global msg

  print('1.5倍速化実行')
  same = False

  if bool(text in msg) == True:
    print('Perfect matching')
    same = True
    text = text[:5] + '。以下略'

  msg.append(text)
  if (same == False) and (message.author.bot == False):
    text = message.author.name + text

  try:
    with open('tmp/voice1.txt', 'w', encoding='shift_jis') as f:
      f.write(text)
    with open('tmp/voice1.txt', 'r', encoding='shift_jis') as f:
      a = f.read()
  except UnicodeEncodeError:
    print("[ERROR] Messages containing Unicode emoji are ignored")
    a = "エラーです。コンソールを確認してください"

  lis = list(a)
  for word in lis:
    if word == '\n':
      lis.remove('\n')
  text = ''.join(lis)


  if "<:" in text:
    custom_emoji_names = re.findall(pattern1, text)
    custom_emoji_ids = re.findall(pattern2, text)

    for i in range(len(custom_emoji_ids)):
      idx = custom_emoji_ids[i].find(":")
      custom_emoji_ids[i] = custom_emoji_ids[i][idx:][1:]

    for i in range(len(custom_emoji_names)):
      custom_ico = custom_emoji_names[i]
      custom_ico_id = custom_emoji_ids[i]
                    
      with open(CUSTOM_EMOJI_DIC_DIR, "r", encoding="UTF-8") as f:
        for line in f:
          if custom_ico in line:
            lis = line.split(":::")
            reading = lis[1] # lis[1][:-1]
            if ".play" in reading:
              reading = reading.split()
              while True:
                if voiceChannel.is_playing() == False:
                  break
                await asyncio.sleep(1)
              voiceChannel.play(FFmpegPCMAudio(f"./mp3/{reading[1]}.mp3", options="-loglevel panic"))
              print(reading[1] + "再生")
              return
            else:
              text = text.replace(f"<:{custom_ico}:{custom_ico_id}>", reading)
            

  if '<@' in text:
    user_ids = re.findall("<@(.*?)>", text)
    for i in range(len(user_ids)):
      user_id = user_ids[i]
      user_name = await client.fetch_user(int(user_id))
      text = text.replace(f"<@{user_id}>", str(user_name)[:-5])
  print(text)
  try:
    with open('tmp/voice1.txt', 'w', encoding='shift_jis') as f:
      f.write(text)
  except UnicodeEncodeError:
    print("Messages containing Unicode emoji are ignored")

  subprocess.run(f'{OPEN_JTALK_EXE} -m {HTS_VOICE_FILE} -x dic -ow tmp/output1.wav tmp/voice1.txt', stderr=subprocess.DEVNULL)
  sound = pydub.AudioSegment.from_wav("tmp/output1.wav")
  sound.export("tmp/out1.mp3", format="mp3")
  baisoku.fast_enc('tmp/out1.mp3')
  os.rename('tmp/baisoku.mp3', f'tmp/{i}.mp3')
  i += 1
  
  while True:
    if voiceChannel.is_playing() == False:
      break
    await asyncio.sleep(1)

  voiceChannel.play(FFmpegPCMAudio(f"tmp/{count}.mp3", options="-loglevel panic"))
  count += 1

async def nomal(text, message, voiceChannel, client):
  global i, count
  global msg

  i = 0
  count = 0
  if message.author.bot != True:
    text = message.author.name + text
  msg.clear()
  for file in glob.glob('tmp/*.mp3'):
    os.remove(file)

  try:
    with open('tmp/voice.txt', 'w', encoding='shift_jis') as f:
      f.write(text)
    with open('tmp/voice.txt', 'r', encoding='shift_jis') as f:
      a = f.read()
  except UnicodeEncodeError:
    print("[ERROR] Messages containing Unicode emoji are ignored")
    a = "エラーです。コンソールを確認してください"
    
  lis = list(a)
  for word in lis:
    if word == '\n':
      lis.remove('\n')
  text = ''.join(lis)


  if "<:" in text:
    custom_emoji_names = re.findall(pattern1, text)
    custom_emoji_ids = re.findall(pattern2, text)

    for i in range(len(custom_emoji_ids)):
      idx = custom_emoji_ids[i].find(":")
      custom_emoji_ids[i] = custom_emoji_ids[i][idx:][1:]

    for i in range(len(custom_emoji_names)):
      custom_ico = custom_emoji_names[i]
      custom_ico_id = custom_emoji_ids[i]
                    
      with open(CUSTOM_EMOJI_DIC_DIR, "r", encoding="UTF-8") as f:
        for line in f:
          if custom_ico in line:
            lis = line.split(":::")
            reading = lis[1]
            if ".play" in reading:
              reading = reading.split()
              voiceChannel.play(FFmpegPCMAudio(f"./mp3/{reading[1]}.mp3", options="-loglevel panic"))
              print(reading[1] + "再生")
              return
            else:
              text = text.replace(f"<:{custom_ico}:{custom_ico_id}>", reading)

  if '<@' in text:
    user_ids = re.findall("<@(.*?)>", text)
    for i in range(len(user_ids)):
      user_id = user_ids[i]
      user_name = await client.fetch_user(int(user_id))
      text = text.replace(f"<@{user_id}>", str(user_name)[:-5])

  print(text)
  with open('tmp/voice.txt', 'w', encoding='shift_jis') as f:
    f.write(text)

  subprocess.run(f'{OPEN_JTALK_EXE} -m {HTS_VOICE_FILE} -x dic -ow tmp/output.wav tmp/voice.txt', stderr=subprocess.DEVNULL)
  sound = pydub.AudioSegment.from_wav("tmp/output.wav")
  sound.export("tmp\out.mp3", format="mp3")
  if (voiceChannel != None):
    voiceChannel.play(FFmpegPCMAudio("tmp/out.mp3", options="-loglevel panic"))