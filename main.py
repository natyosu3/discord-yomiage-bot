"""
制作者:natyosu.zip (natyosu.zip#2308)
python -ver 3.10.3

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
from discord.errors import *
import asyncio
import ctypes
import asyncio
import sys
import os
import dic_mode_cmd
import voice_reproducing_relationship
from config.config import *
from dic_mode_vars import *

kernel32 = ctypes.windll.kernel32
handle = kernel32.GetStdHandle(-11)
kernel32.SetConsoleMode(handle, MODE)

client = discord.Client(intents=discord.Intents.all())

voiceChannel: VoiceChannel = None
join_status = False
on_playing = False
text_ch_id = 0
vc_ch_id = 0


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
  global text_ch_id
  global vc_ch_id
  global dic_mode_vars

  # helpコマンド
  if message.content == HELP_CMD:
    await message.channel.send(HELP_MESSAGE)

  # dic-modeコマンド
  if message.content == DIC_MODE_CMD:
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
  if message.content == JOIN_CMD:
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
  if message.content == LEAVE_CMD:
    if join_status == False:
      await message.channel.send('ボイスチャンネルに参加していません。!joinコマンドを実行して下さい。')
      return

    join_status = False
    dic_mode_vars["dic_mode"] = False
    voiceChannel.stop()
    await voiceChannel.disconnect()
    return

  # playコマンド
  if str(message.content)[0:5] == PLAY_MP3_CMD:
    if voiceChannel.is_playing() == True:
      while True:
        if voiceChannel.is_playing() == False:
          break
        await asyncio.sleep(1)
    play_mp3(message.content)
  
  if message.content == PAUSE_MP3_CMD:
    pause_mp3()

  if message.content == STOP_MP3_CMD:
    stop_mp3()

  if message.content == RESUME_MP3_CMD:
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
        await voice_reproducing_relationship.fast(text=text, message=message, voiceChannel=voiceChannel, client=client)

      else:
        await voice_reproducing_relationship.nomal(text=text, message=message, voiceChannel=voiceChannel, client=client)

def play_mp3(cmd):
  print("MP3ファイル名: " + cmd)
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

def launch_verification():
  if VS_COMPILER_PATH == "NONE":
    print("config.pyにvisual studio compilerのパスを設定してください")
    sys.exit()
  
  os.environ['Path'] += os.pathsep + VS_COMPILER_PATH

if __name__ == '__main__':
  launch_verification()
  client.run(TOKEN)
