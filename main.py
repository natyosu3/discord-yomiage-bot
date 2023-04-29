"""
制作者:natyosu.zip (natyosu.zip#2308)
python -ver 3.11.3

最終更新日:23/04/29

※当スクリプトを用いて発生した,如何なる損害については,制作者は一切の責任を負いません

必須module list
-PyNaCl
-pydub
-discord.py
-pandas
"""

import discord
from discord.channel import VoiceChannel
from discord.player import FFmpegPCMAudio
import pydub
from discord.errors import *
import subprocess
import asyncio
import baisoku
import glob
import os
import ctypes
import re
import asyncio
import dic_mode_cmd
from config.config import *
from dic_mode_vars import *

kernel32 = ctypes.windll.kernel32
handle = kernel32.GetStdHandle(-11)
kernel32.SetConsoleMode(handle, MODE)


client = discord.Client(intents=discord.Intents.all())

voiceChannel: VoiceChannel = None
join_status = False
on_playing = False
msg = []
i = 0
count = 0
text_ch_id = 0
vc_ch_id = 0
pattern1 = "<:(.*?):"
pattern2 = ":(.*?)>"


@client.event
async def on_ready():
    print(f'-------------------------------------\n(※通知) BOT起動\n-------------------------------------')

# チャンネル入退室時の通知処理
@client.event
async def on_voice_state_update(member, before, after):
  global text_ch_id
  global vc_ch_id

  if before.channel != after.channel:
      # 通知メッセージを書き込むテキストチャンネル
      botRoom = client.get_channel(text_ch_id)

      # 入退室を監視する対象のボイスチャンネル
      announceChannelIds = [vc_ch_id, vc_ch_id]

      # 退室通知
      if before.channel is not None and before.channel.id in announceChannelIds:
        print(COLOR_DIC["Cyan"] + "退室通知" + COLOR_DIC["end"] + " : " + member.name + " is disconected from " + before.channel.name)
        await botRoom.send("**" + before.channel.name + "** から、__" + member.name + "__  が抜けました！")

      # 入室通知
      if after.channel is not None and after.channel.id in announceChannelIds:
        print(COLOR_DIC["Cyan"] + "入室通知" + COLOR_DIC["end"] + " : " + member.name + " is conected at " + after.channel.name)
        await botRoom.send("**" + after.channel.name + "** に、__" + member.name + "__  が参加しました！")


@client.event
async def on_message(message):
  global voiceChannel
  global join_status
  global vch
  global msg
  global i, count
  global text_ch_id
  global vc_ch_id
  global dic_mode_vars

  # helpコマンド
  if message.content == ".help":
    await message.channel.send(HELP_MESSAGE)

  # dic-modeコマンド
  if message.content == '.dic-mode':
    await dic_mode_cmd.cmd_call_dic_mode(message)

  # activing dic-mode (if in dic-mode, all msg are ignored)
  if (dic_mode_vars["dic_mode"] == True):
    if (message.author.bot == True):
      return
    await dic_mode_cmd.cmd_call_activing_dic_mode(message)
    return

  # vcチャンネル以外は無視(join後)
  if (join_status == True) and (message.content != '.join') and (message.channel.id != text_ch_id):
    return

  # joinコマンド実行時
  if message.content == '.join':
    # コマンド実行者がボイスチャンネルに参加していない場合
    if message.author.voice == None:
      await message.channel.send('joinコマンドはボイスチャンネルに参加してから実行して下さい')
      return
    
    join_status = True
    vch = client.get_channel(message.author.voice.channel.id)
    text_ch = client.get_channel(message.channel.id)
    text_ch_id = message.channel.id
    vc_ch_id = message.author.voice.channel.id
    print(f'-----------------------------\n' + 'テキストチャンネル名:' + str(text_ch) + '\n' + '-----------------------------')

    # botが既に入室済みの場合
    if client.user.id in vch.voice_states.keys():
      print('(ERROR) Already connected to a voice channel.')
      await message.channel.send('もう参加してるぞ!')
      return

    # 接続済みだった場合
    if (voiceChannel != None):
      if (voiceChannel.is_connected()) == True:
        await voiceChannel.move_to(message.author.voice.channel)

    # join voicechannel
    voiceChannel = await VoiceChannel.connect(vch)

  # getoutコマンド実行時
  if message.content == '.getout':
    if join_status == False:
      await message.channel.send('ボイスチャンネルに参加していません。!joinコマンドを実行して下さい。')
      return

    join_status = False
    dic_mode_vars["dic_mode"] = False
    voiceChannel.stop()
    await voiceChannel.disconnect()
    return

  # playコマンド
  if str(message.content)[0:5] == '.play':
    if voiceChannel.is_playing() == True:
      while True:
        if voiceChannel.is_playing() == False:
          break
        await asyncio.sleep(1)
    play_mp3(message.content)
  
  if message.content == '.pause':
    pause_mp3()

  if message.content == '.stop':
    stop_mp3()

  if message.content == '.resume':
    resume_mp3()

  # join済みの場合
  if join_status == True:
    # プレフィックスの不適切な利用を無視
    if str(message.content)[0] == '.':
      return
    # botのみチャンネルに残っている場合
    if len(vch.voice_states.keys()) == 1:
      join_status = False
      dic_mode_vars["dic_mode"] = False
      voiceChannel.stop()
      await message.channel.send('読み上げ君が退出しました')
      await voiceChannel.disconnect()
      return

    text = message.content

    if text[:4] == 'http':
      print('url')
      text = 'URL'
    
    if (voiceChannel != None):
      if voiceChannel.is_playing() == True:
        print('1.5倍速化実行')
        same = False

        if bool(text in msg) == True:
          print('Perfect matching')
          same = True
          text = text[:5] + '。以下略'

        msg.append(text)
        if (same == False) and (message.author.bot == False):
          text = message.author.name + text


        with open('tmp/voice1.txt', 'w', encoding='shift_jis') as f:
          f.write(text)
        with open('tmp/voice1.txt', 'r', encoding='shift_jis') as f:
          a = f.read()
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
                    voiceChannel.play(FFmpegPCMAudio(f"./mp3/{reading[1]}.mp3"))
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
        with open('tmp/voice1.txt', 'w', encoding='shift_jis') as f:
          f.write(text)

        subprocess.run(r'tmp\open_jtalk.exe -m tmp\mei_happy.htsvoice -x dic -ow tmp\output1.wav tmp\voice1.txt')
        sound = pydub.AudioSegment.from_wav("tmp/output1.wav")
        sound.export("tmp/out1.mp3", format="mp3")
        baisoku.fast_enc('tmp/out1.mp3')
        os.rename('tmp/baisoku.mp3', f'tmp/{i}.mp3')
        i += 1
        
        while True:
          if voiceChannel.is_playing() == False:
            break
          await asyncio.sleep(1)

        voiceChannel.play(FFmpegPCMAudio(f"tmp/{count}.mp3"))
        count += 1

      else:
        i = 0
        count = 0
        if message.author.bot != True:
          text = message.author.name + text
        msg.clear()
        for file in glob.glob('tmp/*.mp3'):
          os.remove(file)

        with open('tmp/voice.txt', 'w', encoding='shift_jis') as f:
          f.write(text)
        with open('tmp/voice.txt', 'r', encoding='shift_jis') as f:
          a = f.read()
          
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
                    voiceChannel.play(FFmpegPCMAudio(f"./mp3/{reading[1]}.mp3"))
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
        
        subprocess.run(r'tmp\open_jtalk.exe -m tmp\mei_happy.htsvoice -x dic -ow tmp\output.wav tmp\voice.txt')
        sound = pydub.AudioSegment.from_wav("tmp/output.wav")
        sound.export("tmp\out.mp3", format="mp3")
        if (voiceChannel != None):
          voiceChannel.play(FFmpegPCMAudio("tmp/out.mp3"))

def play_mp3(cmd):
  global on_playing
  on_playing = True
  print(cmd)
  target = ' '
  idx = cmd.find(target)
  track_name_mp3 = cmd[idx+1:]

  print(track_name_mp3)
  voiceChannel.play(FFmpegPCMAudio(f"./mp3/{track_name_mp3}.mp3"))

def pause_mp3():
  voiceChannel.pause()

def stop_mp3():
  voiceChannel.stop()

def resume_mp3():
  voiceChannel.resume()


if __name__ == '__main__':
  client.run(TOKEN)