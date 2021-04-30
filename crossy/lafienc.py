import os
import sys
import colorama #to get, use $pip3 install colorama
from colorama import Fore, Back, Style
colorama.init()

class laboriously_find_encoding:
  def __init__(self, verbosity):
    self.skip_exts = set()
    self.load_skip_exts()
    self.verbose = verbosity
    
  def load_skip_exts(self):
    with open("skipexts.txt", "r") as orf:
      for line in orf:
        line = line.strip()
        try:
          if line[0] == "#":
            pass
          else:
            self.skip_exts |= set([ext for ext in line.split(" ") if len(ext)> 0])
        except:
          sys.exit(f"{Fore.RED}fix incorrect syntax in skipexts.txt {Style.BRIGHT}>{line}<{Style.RESET_ALL}")

  def get_safe_enc(self, path):
    if os.path.splitext(path)[1].lower() in self.skip_exts:
      if self.verbose:
        print(f" {Fore.RED}extension-skipping {Style.BRIGHT}>{os.path.splitext(path)[1].lower()}<{Style.RESET_ALL}")
      return None
    if ".DS_Store" in path:
      return None
    encodings = ['utf-8', 'ascii', 'utf-16-be', 'cp1251', 'latin_1', 'shift_jis', 'cp1252' ]
    for e in encodings:
      try:
        #tl;dr- The code in the 5 lines below is ugly, but it works.
        #Whatever the time cost of this is, it is the only way I've found to
        #blindly open a directory, look at every file, and not crash at some
        #point due to an encoding error.  I've lost hours due to this, and its
        #better just to get the awful thing done right up front.
        #
        #Algorythm:
        #  - open a file, read each line until the end as fast as possible
        #  - if no exceptions are raised, this encoding may or may not be correct,
        #    but it is safe to open using it.
        #  - the method is greedy, on the first successful comptletion, it
        #    returns that encoding
        #    -- due to this, the order of encodings impacts speed; arrange them
        #       in descending order from most likely to least and don't use a set
        for line in open(path, 'r', encoding=e):
          pass
        if self.verbose:
          print(f" {Fore.CYAN}opens as {Style.BRIGHT}{e}{Style.RESET_ALL}")
        return e
      except:
        continue
    if self.verbose:
      print(f" {Fore.RED}{Style.BRIGHT}encoding insantiy...not able to safely open{Style.RESET_ALL}")
    return None
