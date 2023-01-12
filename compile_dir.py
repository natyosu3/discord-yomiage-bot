from subprocess import *
from os import *

def compile():
  chdir("make_dic")
  print("run compile")
  call(".\\Community\\VC\\Auxiliary\\Build\\vcvars64.bat", stdout=DEVNULL)
  call("nmake .\\Makefile.mak", stdout=DEVNULL, stderr=DEVNULL)
  print("finish compile")
  chdir("..")
