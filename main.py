"""
制作者:natyosu.zip (natyosu.zip#2308)
python -ver 3.7.9

最終更新日:23/01/11

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
import csv_dic
import re
 
ENABLE_PROCESSED_OUTPUT = 0x0001
ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
MODE = ENABLE_PROCESSED_OUTPUT + ENABLE_WRAP_AT_EOL_OUTPUT + ENABLE_VIRTUAL_TERMINAL_PROCESSING
 
kernel32 = ctypes.windll.kernel32
handle = kernel32.GetStdHandle(-11)
kernel32.SetConsoleMode(handle, MODE)


client = discord.Client(intents=discord.Intents.all())
TOKEN = 'TOKENを入力 ※取り扱い注意'


color_dic = {"black":"\033[30m", "red":"\033[31m", "green":"\033[32m", "yellow":"\033[33m", "blue":"\033[34m", "Cyan":"\033[36m", "end":"\033[0m"}
voiceChannel: VoiceChannel
status = False
dic_mode = False
on_playing = False
msg = []
i = 0
count = 0
text_ch_id = 0
vc_ch_id = 0
regi_status = False
del_status = False
c_regi_status = False
custom_emoji_dic = "tmp/custom_emoji_dic.txt"
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
        print(color_dic["Cyan"] + "退室通知" + color_dic["end"] + " : " + member.name + " is disconected from " + before.channel.name)
        await botRoom.send("**" + before.channel.name + "** から、__" + member.name + "__  が抜けました！")

      # 入室通知
      if after.channel is not None and after.channel.id in announceChannelIds:
        print(color_dic["Cyan"] + "入室通知" + color_dic["end"] + " : " + member.name + " is conected at " + after.channel.name)
        await botRoom.send("**" + after.channel.name + "** に、__" + member.name + "__  が参加しました！")


@client.event
async def on_message(message):
  global voiceChannel
  global status
  global vch
  global msg
  global i, count
  global text_ch_id
  global vc_ch_id
  global dic_mode, word, reading, regi_status, del_status, c_regi_status, track_name

  # helpコマンド
  if message.content == ".help":
    help_msg = ("```--BOTコマンド一覧--\n<>は不要です\n<.join> ボイスチャンネルにBOTが接続します。 ※ボイスチャンネルに接続した状態で実行して下さい。\n<.play <mp3ファイル名>> mp3ファイルが再生されます。" + "\n<.stop> 再生中のmp3, 読み上げが停止します。\n<.pause> 再生中のmp3, 読み上げを一時停止します。"
    "\n<.resume> 一時停止した音声再生を再開します。```" + "```<.dic-mode> 辞書modeになります。※以下7つのコマンドは辞書mode中のみ実行可能です。\n<.out>辞書mode終了\n<.list> ユーザ辞書登録情報一覧を表示します。" + "\n<.regi <登録したい単語> <読み方>> ユーザ辞書に単語を登録できます。読み方は、平仮名かカタカナで入力して下さい。"
    "\n<.del <削除したい単語>>ユーザ辞書から単語を削除できます ※英数字は半角で入力して下さい。" + "\n<.c-regi <登録したいカスタム絵文字の名称> <読み方>> カスタム絵文字に対する読み方を設定できます。読み方に<.play <mp3ファイル名>>を設定するとカスタム絵文字着信時にmp3ファイルが流れます。\n<.c-list> 登録済みカスタム絵文字辞書一覧を表示します。"
    "\n<.c-del <削除したいカスタム絵文字の名称>> カスタム絵文字辞書から削除されます```")
    await message.channel.send(help_msg)

  # dic-modeコマンド
  if message.content == '.dic-mode':
    if dic_mode == True:
      await message.channel.send("既に辞書modeです")
      return
    dic_mode = True
    print(color_dic['red'] + "ACTIVATE" + color_dic['end'] + ": DIC-mode")
    await message.channel.send('辞書modeになりました。\n**※辞書mode中は読み上げ機能,mp3再生機能が利用出来ません。<.out>で辞書mode解除**')


  # activing dic-mode
  if (dic_mode == True) and (message.author.bot != True):

    # registコマンド
    if ('.regi' in message.content):
      cmd = message.content.split()
      word = cmd[1]
      reading = cmd[2]

      regi_status = True

      await message.channel.send(f'登録内容\n登録単語:{word}\n読み方:{reading}\nでよろしいですか?\n問題なければ<yes>,訂正が必要でしたら<no>を入力して下さい。')

    # listコマンド
    elif ('.list' in message.content):
      with open("tmp/user_dic.txt", "r", encoding="UTF-8") as f:
        tex = f.read()
        await message.channel.send("ユーザ辞書-登録済み一覧 ※単語(全角):::読み方(カタカナ)\n-------------------\n" + tex + "-------------------")

    # del <単語>
    elif ('.del' == message.content[:4]) and (del_status == False):
      cmd = message.content.split()
      del_word = cmd[1]
      await message.channel.send("削除実行中...")
      del_status = True
      csv_dic.del_csv(del_word)
      del_status = False
      await message.channel.send("削除完了しました。")

    # yes
    elif ('yes' in message.content) and (regi_status == True):
      await message.channel.send("辞書登録を開始します")
      csv_dic.add_csv(word, reading)
      regi_status = False
      await message.channel.send("辞書登録完了")

    # no
    elif ('no' in message.content) and (regi_status == True):
      regi_status = False
      await message.channel.send("再度<.regi>コマンドを実行して下さい")
      return

    # c-list
    elif message.content == ".c-list":
      with open(custom_emoji_dic, "r", encoding="UTF-8") as f:
        tex = f.read()
        await message.channel.send("カスタム絵文字辞書-登録済み一覧 ※単語(半角):::読み方\n-------------------\n" + tex + "-------------------")

    # c-del
    elif message.content[:6] == ".c-del":
      char_remove = message.content[7:]
      os.rename(custom_emoji_dic, custom_emoji_dic + '.bak')
      with open(custom_emoji_dic, "w", encoding="UTF-8") as f:
        for line in open(custom_emoji_dic + ".bak", "r", encoding="UTF-8"):
          if not char_remove in line:
            f.write(line)
      os.remove(custom_emoji_dic + '.bak')
      await message.channel.send("カスタム絵文字,辞書登録解除完了")

    # regi custom_emoji
    elif (".c-regi" in message.content):
      c_regi_status = True
      cmd = message.content.split()
      word = cmd[1]
      reading = cmd[2]
      if ".play" in reading:
        track_name = cmd[3]
        await message.channel.send(f'登録内容\n登録絵文字名(半角):{word}\n音声再生:{reading}:{track_name}\nでよろしいですか?\n問題なければ<yes>,訂正が必要でしたら<no>を入力して下さい。')        
      else:
        await message.channel.send(f'登録内容\n登録絵文字名(半角):{word}\n読み方:{reading}\nでよろしいですか?\n問題なければ<yes>,訂正が必要でしたら<no>を入力して下さい。')

    # yes
    elif ('yes' in message.content) and (c_regi_status == True):
      if ".play" in reading:
        with open(custom_emoji_dic, "a", encoding="UTF-8") as f:
          f.write(word + ":::" + reading + " " + track_name + "\n")
        await message.channel.send("カスタム絵文字,辞書登録完了")      
        c_regi_status = False
      else:
        with open(custom_emoji_dic, "a", encoding="UTF-8") as f:
          f.write(word + ":::" + reading + "\n")
        await message.channel.send("カスタム絵文字,辞書登録完了")      
        c_regi_status = False

    # no
    elif ('no' in message.content) and (c_regi_status == True):
      c_regi_status = False
      await message.channel.send("再度<.c-regi>コマンドを実行して下さい")
      return

    # outコマンド
    elif message.content == ".out":
      dic_mode = False
      print(color_dic['red'] + "INACTIVATE" + color_dic['end'] + ": DIC-mode")
      await message.channel.send("辞書mode終了しました")

    else:
      return

  if dic_mode == True:
    return

  # vcチャンネル以外は無視(join後)
  if (status == True) and (message.content != '.join') and (message.channel.id != text_ch_id):
    return

  # joinコマンド実行時
  if message.content == '.join':
    if message.author.voice == None:
      await message.channel.send('joinコマンドはボイスチャンネルに参加してから実行して下さい')
      return
    
    status = True
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
    try:
      if (voiceChannel.is_connected()) == True:
        await voiceChannel.move_to(message.author.voice.channel)
    except NameError:
      None

    # join voicechannel
    voiceChannel = await VoiceChannel.connect(message.author.voice.channel)
    return

  # getoutコマンド実行時
  elif message.content == '.getout':
    if status == False:
      await message.channel.send('ボイスチャンネルに参加していません。!joinコマンドを実行して下さい。')
      return

    status = False
    dic_mode = False
    voiceChannel.stop()
    await voiceChannel.disconnect()
    return

  # playコマンド
  elif str(message.content)[0:5] == '.play':
    if voiceChannel.is_playing() == True:
      while True:
        if voiceChannel.is_playing() == False:
          break
        await asyncio.sleep(1)
    play_mp3(message.content)
  
  elif message.content == '.pause':
    pause_mp3()

  elif message.content == '.stop':
    stop_mp3()

  elif message.content == '.resume':
    resume_mp3()

  # join済みの場合
  if status == True:
    # botのみチャンネルに残っている場合
    if str(message.content)[0] == '.':
      return
    if len(vch.voice_states.keys()) == 1:
      status = False
      dic_mode = False
      voiceChannel.stop()
      await message.channel.send('読み上げ君が退出しました')
      await voiceChannel.disconnect()

    else:
      text = message.content
      if text[:4] == 'http':
        print('url')
        text = 'URL'

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
          custom_ico_names = re.findall(pattern1, text)
          custom_ico_ids = re.findall(pattern2, text)

          for i in range(len(custom_ico_ids)):
            idx = custom_ico_ids[i].find(":")
            custom_ico_ids[i] = custom_ico_ids[i][idx:][1:]

          for i in range(len(custom_ico_names)):
            custom_ico = custom_ico_names[i]
            custom_ico_id = custom_ico_ids[i]
                          
            with open(custom_emoji_dic, "r", encoding="UTF-8") as f:
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

        subprocess.run(f'tmp/open_jtalk.exe -m tmp/mei_happy.htsvoice -x dic -ow tmp/output1.wav tmp/voice1.txt')
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
          custom_ico_names = re.findall(pattern1, text)
          custom_ico_ids = re.findall(pattern2, text)

          for i in range(len(custom_ico_ids)):
            idx = custom_ico_ids[i].find(":")
            custom_ico_ids[i] = custom_ico_ids[i][idx:][1:]

          for i in range(len(custom_ico_names)):
            custom_ico = custom_ico_names[i]
            custom_ico_id = custom_ico_ids[i]
                          
            with open(custom_emoji_dic, "r", encoding="UTF-8") as f:
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
        
        subprocess.run(f'tmp/open_jtalk.exe -m tmp/mei_happy.htsvoice -x dic -ow tmp/output.wav tmp/voice.txt')
        sound = pydub.AudioSegment.from_wav("tmp/output.wav")
        sound.export("tmp/out.mp3", format="mp3")
        voiceChannel.play(FFmpegPCMAudio("tmp/out.mp3"))

def play_mp3(cmd):
  global on_playing
  on_playing = True
  print(cmd)
  target = ' '
  idx = cmd.find(target)
  track_name = cmd[idx+1:]

  print(track_name)
  voiceChannel.play(FFmpegPCMAudio(f"./mp3/{track_name}.mp3"))

def pause_mp3():
  voiceChannel.pause()

def stop_mp3():
  voiceChannel.stop()

def resume_mp3():
  voiceChannel.resume()


if __name__ == '__main__':
  client.run(TOKEN)
