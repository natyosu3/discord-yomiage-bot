import os
import csv_dic
from config.config import *
from dic_mode_vars import *


# call dic-mode
async def cmd_call_dic_mode(message):
  global dic_mode_vars

  if dic_mode_vars["dic_mode"] == True:
    await message.channel.send("既に辞書modeです")
    return
  dic_mode_vars["dic_mode"] = True
  print(COLOR_DIC['red'] + "ACTIVATE" + COLOR_DIC['end'] + ": DIC-mode")
  await message.channel.send('辞書modeになりました。\n**※辞書mode中は読み上げ機能,mp3再生機能が利用出来ません。<.out>で辞書mode解除**')


# activing dic-mode
async def cmd_call_activing_dic_mode(message):
  global dic_mode_vars

  # registコマンド
  if ('.regi' in message.content):
    cmd = message.content.split()
    dic_mode_vars["regi_word"] = cmd[1]
    dic_mode_vars["regi_reading"] = cmd[2]

    dic_mode_vars["regi_status"] = True

    await message.channel.send(f'登録内容\n登録単語:{dic_mode_vars["regi_word"]}\n読み方:{dic_mode_vars["regi_reading"]}\nでよろしいですか?\n問題なければ<yes>,訂正が必要でしたら<no>を入力して下さい。')

  # listコマンド
  elif ('.list' in message.content):
    with open("tmp/user_dic.txt", "r", encoding="UTF-8") as f:
      tex = f.read()
      await message.channel.send("ユーザ辞書-登録済み一覧 ※単語(全角):::読み方(カタカナ)\n-------------------\n" + tex + "-------------------")

  # del <単語>
  elif ('.del' == message.content[:4]) and (dic_mode_vars["del_status"] == False):
    cmd = message.content.split()
    del_word = cmd[1]
    await message.channel.send("削除実行中...")
    dic_mode_vars["del_status"] = True
    csv_dic.del_csv(del_word)
    dic_mode_vars["del_status"] = False
    await message.channel.send("削除完了しました。")

  # yes
  elif ('yes' in message.content) and (dic_mode_vars["regi_status"] == True):
    await message.channel.send("辞書登録を開始します")
    csv_dic.add_csv(dic_mode_vars["regi_word"], dic_mode_vars["regi_reading"])
    dic_mode_vars["regi_status"] = False
    await message.channel.send("辞書登録完了")

  # no
  elif ('no' in message.content) and (dic_mode_vars["regi_status"] == True):
    dic_mode_vars["regi_status"] = False
    await message.channel.send("再度<.regi>コマンドを実行して下さい")
    return

  # c-list
  elif message.content == ".c-list":
    with open(CUSTOM_EMOJI_DIC_DIR, "r", encoding="UTF-8") as f:
      tex = f.read()
      await message.channel.send("カスタム絵文字辞書-登録済み一覧 ※単語(半角):::読み方\n-------------------\n" + tex + "-------------------")

  # c-del
  elif message.content[:6] == ".c-del":
    char_remove = message.content[7:]
    os.rename(CUSTOM_EMOJI_DIC_DIR, CUSTOM_EMOJI_DIC_DIR + '.bak')
    with open(CUSTOM_EMOJI_DIC_DIR, "w", encoding="UTF-8") as f:
      for line in open(CUSTOM_EMOJI_DIC_DIR + ".bak", "r", encoding="UTF-8"):
        if not char_remove in line:
          f.write(line)
    os.remove(CUSTOM_EMOJI_DIC_DIR + '.bak')
    await message.channel.send("カスタム絵文字,辞書登録解除完了")

  # regi custom_emoji
  elif (".c-regi" in message.content):
    dic_mode_vars["c_regi_status"] = True
    cmd = message.content.split()
    dic_mode_vars["regi_word"] = cmd[1]
    dic_mode_vars["regi_reading"] = cmd[2]
    if ".play" in dic_mode_vars["regi_reading"]:
      dic_mode_vars["emoji_cus_mp3_file_name"] = cmd[3]
      await message.channel.send(f'登録内容\n登録絵文字名(半角):{dic_mode_vars["regi_word"]}\n音声再生:{dic_mode_vars["regi_reading"]}:{dic_mode_vars["emoji_cus_mp3_file_name"]}\nでよろしいですか?\n問題なければ<yes>,訂正が必要でしたら<no>を入力して下さい。')        
    else:
      await message.channel.send(f'登録内容\n登録絵文字名(半角):{dic_mode_vars["regi_word"]}\n読み方:{dic_mode_vars["regi_reading"]}\nでよろしいですか?\n問題なければ<yes>,訂正が必要でしたら<no>を入力して下さい。')

  # yes
  elif ('yes' in message.content) and (dic_mode_vars["c_regi_status"] == True):
    if ".play" in dic_mode_vars["regi_reading"]:
      with open(CUSTOM_EMOJI_DIC_DIR, "a", encoding="UTF-8") as f:
        f.write(dic_mode_vars["regi_word"] + ":::" + dic_mode_vars["regi_reading"] + " " + dic_mode_vars["emoji_cus_mp3_file_name"] + "\n")
      await message.channel.send("カスタム絵文字,辞書登録完了")      
      dic_mode_vars["c_regi_status"] = False
    else:
      with open(CUSTOM_EMOJI_DIC_DIR, "a", encoding="UTF-8") as f:
        f.write(dic_mode_vars["regi_word"] + ":::" + dic_mode_vars["regi_reading"] + "\n")
      await message.channel.send("カスタム絵文字,辞書登録完了")      
      dic_mode_vars["c_regi_status"] = False

  # no
  elif ('no' in message.content) and (dic_mode_vars["c_regi_status"] == True):
    dic_mode_vars["c_regi_status"] = False
    await message.channel.send("再度<.c-regi>コマンドを実行して下さい")
    return 

  # outコマンド
  elif message.content == ".out":
    dic_mode_vars["dic_mode"] = False
    print(COLOR_DIC['red'] + "INACTIVATE" + COLOR_DIC['end'] + ": DIC-mode")
    await message.channel.send("辞書mode終了しました")

  else:
    # retrun true -> in main loop retrun
    return True