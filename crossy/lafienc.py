import os
import sys
import colorama
from colorama import Fore, Back, Style
colorama.init()

#the class name says what this does
class laboriously_find_encoding:
  def __init__(self, verbosity):
    self.skip_exts = set()
    self.load_skip_exts()
    self.verbose = verbosity

  #this loads extensions which the script will skip, because they are not
  #appropriate to be read (e.g. .docx or .pdf).
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

  #this returns a safe encoding with which to open a file.  It skips files with
  #extensions which are defined in skipexts.txt.
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
        #tl;dr- Whatever the time cost of this is, it works.
        #
        #Algorithm:
        #  - open a file, read each line until the end as fast as possible
        #  - if no exceptions are raised, this encoding may or may not be correct,
        #    but it is safe to open using it.
        #  - the method is greedy, on the first successful completion, it
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
      print(f" {Fore.RED}{Style.BRIGHT}encoding insanity...not able to safely open{Style.RESET_ALL}")
    return None
