import shutil
import jaconv
import compile_dir
import os
import subprocess
import pandas as pd
import time


FULLWIDTH_DIGITS = "０１２３４５６７８９"
FULLWIDTH_ALPHABET = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
FULLWIDTH_PUNCTUATION = "！＂＃＄％＆＇（）＊＋，－．／：；＜＝＞？＠［＼］＾＿｀｛｜｝～　"
FULLWIDTH_ALPHANUMERIC = FULLWIDTH_DIGITS + FULLWIDTH_ALPHABET
FULLWIDTH_ALL = FULLWIDTH_ALPHANUMERIC + FULLWIDTH_PUNCTUATION

HALFWIDTH_DIGITS = "0123456789"
HALFWIDTH_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
HALFWIDTH_PUNCTUATION = "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ "
HALFWIDTH_ALPHANUMERIC = HALFWIDTH_DIGITS + HALFWIDTH_ALPHABET
HALFWIDTH_ALL = HALFWIDTH_ALPHANUMERIC + HALFWIDTH_PUNCTUATION

# 数字、アルファベットを半角に変換する。
conv_map = str.maketrans(HALFWIDTH_ALPHANUMERIC, FULLWIDTH_ALPHANUMERIC)
user_dic = "tmp/user_dic.txt"

def add_csv(word, reading):
  word = word.translate(conv_map)
  reading = jaconv.hira2kata(reading)
  linecsv = f"{word},,,1,名詞,一般,*,*,*,*,{word},{reading},{reading},0/1,*"
  
  with open("tmp/user_dic.txt", "a", encoding="UTF-8") as f:
    text = f"{word}:::{reading}\n"
    f.write(text)

  # print(linecsv)

  with open('make_dic/unidic-csj.csv', mode='a', encoding="UTF-8") as f:
    print(linecsv, file=f)
  compile_dir.compile()
  time.sleep(1)
  shutil.move("make_dic/matrix.bin", "dic/matrix.bin")
  shutil.move("make_dic/sys.dic", "dic/sys.dic")
  shutil.move("make_dic/char.bin", "dic/char.bin")
  shutil.move("make_dic/unk.dic", "dic/unk.dic")


def del_csv(delword):
  char_remove = delword.translate(conv_map)

  os.rename(user_dic, user_dic + '.bak')
  with open(user_dic, "w", encoding="UTF-8") as f:
    for line in open(user_dic + ".bak", "r", encoding="UTF-8"):
      if not char_remove in line:
        f.write(line)
  os.remove(user_dic + '.bak')

  p = subprocess.run("find /v /c \"\" make_dic/unidic-csj.csv",capture_output=True).stdout

  p = str(p)
  idx = p.find("CSV: ")
  r = p[idx+5:-5]

  df = pd.read_csv("make_dic/unidic-csj.csv")
  for i in range(302156, int(r) - 1):
    df.drop(index=i, inplace=True)
  df.to_csv('make_dic/unidic-csj.csv', index=False)

  with open(user_dic, "r", encoding="UTF-8") as f:
    for line in f:
      lis = line.split(":::")
      word = lis[0]
      reading = lis[1][:-1]
      linecsv = f"{word},,,1,名詞,一般,*,*,*,*,{word},{reading},{reading},0/1,*"
      with open('make_dic/unidic-csj.csv', mode='a', encoding="UTF-8") as f:
        print(linecsv, file=f)
  compile_dir.compile()
  time.sleep(3)
  shutil.move("make_dic/matrix.bin", "./dic/matrix.bin")
  shutil.move("make_dic/sys.dic", "./dic/sys.dic")
  shutil.move("make_dic/char.bin", "dic/char.bin")
  shutil.move("make_dic/unk.dic", "dic/unk.dic")

  

if __name__ == '__main__':
  del_csv(delword="natyosu")