from subprocess import *
from os import *

def compile():
  print("run compile")
  chdir("make_dic")
  call("nmake Makefile.mak", stderr=DEVNULL, stdout=DEVNULL)
  print("finish compile")
  chdir("..")
