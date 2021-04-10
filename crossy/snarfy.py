#tl;dr- snarf is the tricky part.
#
#The algorythm is:
# - open a file with a safe encoding
# - for each line in the file:
#   -- break the line into "nuggets"--discreet chunks of text which may contain
#      a value I care about--using whitespace
#   -- analyze each nugget and store the ones which get tagged; tag options are:
#      --- IPv4, IPv6 (very accurate results)
#      --- email-ish strings (medium junk to useful ratio)
#      --- path/url-ish strings (high junk to useful ratio)
#      --- there is the option to store every word found
#   -- store the data into dictionaries where I can pivot from word to file and
#      vice versa


import ipaddress
import colorama #to get, use $pip install colorama
from colorama import Fore, Back, Style
colorama.init()
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL
#
#######################################################################

from pynugget import nugget

class snarf:
  def __init__(self, print_arg):
    self.print_all = print_arg
    self.nug2doc = {} #all the data goes into here and ...
    self.doc2nug = {} #here.
    self.legal_email_chars = set([c for c in "@.abcdefghijklmnopqrstuvwxyz_0123456789+-~"])
  def __repr__self(self):
    return f"number of docs processed: {len(doc2nug.keys())}\nnumber of nuggets found: {len(nug2doc.keys())}\nhash of class instance: {hash(self)}"
  def __str__(self):
    output = "*" *80 + "\n"
    for nugget, docs in self.nug2doc.items():
      if self.print_all or len(docs) > 1:
        output += f"{nugget}:\n"
        for doc in docs:
          output += f"  {doc}\n"
    return output

  def csv(self): #print for use in an Excel pivot table
    output = '\n\n"TYPE","VALUE","FILE"\n'
    for nugget, docs in self.nug2doc.items():
      if self.print_all or len(docs) > 1:
        for doc in docs:
          output += f'{nugget.csv()},"{doc}"\n'
    return output


  def file(self, path, safe_enc, args):
    if path not in self.doc2nug.keys():
      self.doc2nug[path] = set()
    with open(path, "r", encoding=safe_enc) as orf:
      for row in orf:
        self.doc2nug[path] |= self.process_row(row, args)
    for nug in self.doc2nug[path]:
      if nug not in self.nug2doc.keys():
        self.nug2doc[nug] = set()
      self.nug2doc[nug].add(path)
      
  def process_row(self, row, args):
    snarfed = set()
    raw_nuggets = self.make_nuggets(row)
    if args.get_ips:
      snarfed |= self.snarf_ips(raw_nuggets)
    if args.get_emails:
      snarfed |= self.snarf_emails(raw_nuggets)
    if args.get_paths:
      snarfed |= self.snarf_paths(raw_nuggets)
    if args.get_all:
      snarfed |= self.snarf_all(raw_nuggets)
    return snarfed
 
  def make_nuggets(self, row):
    nugget_set = set()
    row = row.strip()
    #this gets rid of common escape sequences (e.g. annoying bell dings)
    #thank you to: hxxps://stackoverflow.com/questions/8115261/how-to-remove-all-the-escape-sequences-from-a-list-of-strings
    escapes = "".join([chr(char) for char in range(1, 32)])
    translator = str.maketrans("", "", escapes)
    row = row.translate(translator)
    #finding paths/urls is messy; this adds a nugget that may be a url or path
    #(windows uses annoying \)
    if "/" in row or "\\" in row:
      new_row = row
      for c in ":\"'\t": #if this is in the line, turn it into a " " for splitting
        new_row = new_row.replace(c, " ")
        nugget_set |= set([nug for nug in row.split(" ") if "/" in nug or "\\" in nug])
    #after saving possible, paths, break the line into the smallest nuggets possible
    for c in ",!$%&*(){}[]<>?;:|/\`\\\"'\t": #split on all of these
      row = row.replace(c, " ")
    nugs = set([n for n in row.split(" ") if len(n)>0])
    end_cl = ".:;,!?-=" #clean endings so that "word." is the same as "word"
    for nug in nugs:
      if nug[-1] in end_cl:
        nug = nug[:-1]
      if len(nug) > 1:
        nugget_set.add(nug)
    return(nugget_set)

  def snarf_ips(self, nugs):
    '''ddddd
    this is accurate regex for IPv4:
    ^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
    (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
    (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
    (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
    and for IPv6:
    (\A([0-9a-f]{1,4}:){1,1}(:[0-9a-f]{1,4}){1,6}\Z)|
    (\A([0-9a-f]{1,4}:){1,2}(:[0-9a-f]{1,4}){1,5}\Z)|
    (\A([0-9a-f]{1,4}:){1,3}(:[0-9a-f]{1,4}){1,4}\Z)|
    (\A([0-9a-f]{1,4}:){1,4}(:[0-9a-f]{1,4}){1,3}\Z)|
    (\A([0-9a-f]{1,4}:){1,5}(:[0-9a-f]{1,4}){1,2}\Z)|
    (\A([0-9a-f]{1,4}:){1,6}(:[0-9a-f]{1,4}){1,1}\Z)|
    (\A(([0-9a-f]{1,4}:){1,7}|:):\Z)|
    (\A:(:[0-9a-f]{1,4}){1,7}\Z)|
    (\A((([0-9a-f]{1,4}:){6})(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})\Z)|
    (\A(([0-9a-f]{1,4}:){5}[0-9a-f]{1,4}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})\Z)|
    (\A([0-9a-f]{1,4}:){5}:[0-9a-f]{1,4}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|
    (\A([0-9a-f]{1,4}:){1,1}(:[0-9a-f]{1,4}){1,4}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|
    (\A([0-9a-f]{1,4}:){1,2}(:[0-9a-f]{1,4}){1,3}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|
    (\A([0-9a-f]{1,4}:){1,3}(:[0-9a-f]{1,4}){1,2}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|
    (\A([0-9a-f]{1,4}:){1,4}(:[0-9a-f]{1,4}){1,1}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|
    (\A(([0-9a-f]{1,4}:){1,5}|:):(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|
    (\A:(:[0-9a-f]{1,4}){1,5}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)
    '''
    ips = set()
    for nug in nugs:
      try:
        ip = ipaddress.ip_address(nug)  #built-in python function
        if ip.is_loopback:              #this is not what I'm looking for...
          continue
        elif ip.version == 6:
          ips.add(nugget("IPV6", ip.exploded))
        elif ip.version == 4:
          ips.add(nugget("IPV4", ip.exploded))
      except:
        continue
    return ips

  def snarf_emails(self, nugs):
    '''
    this is a regex for email:
    (?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])
    '''
    emails = set()
    for nug in nugs:
      if len(nug) < 4:   #ignore anything below this size
        continue
      if nug.count("@") != 1:  #there can only be one @ in the nugget
        continue
      #there cannot be an illegal char in the word (this is the slow part)
      skip = False
      for char in nug:
        if char.lower() not in self.legal_email_chars:
          skip = True
          break #if illegal char found, break and skip nug
      if skip:
        continue
      #at this point we have something like a twitter/telegaram or a jabber/email
      chunks = nug.split("@")
      if len(chunks[0]) == 0:
        #these are twitterish words, e.g. @coolio, @uncoolio, etc
        emails.add(nugget("SOCL", nug))
      else:
        #one last check for jabber/emailish words and add if it passes
        if "." in chunks[1]:
          emails.add(nugget("EML_", nug)) #e.g. a@b.c passes
    return emails

  def snarf_paths(self, nugs):
    '''
    this is a regex for a filepath:
    ^(.*/)([^/]*)$
    I'll just do it my own way.
    '''
    urls = set()
    for nug in nugs:
      if(nug.count("/") > 1 or nug.count("\\") > 1):
        if nug.count(">") == nug.count("<"): #this tries to keep out xml/html
          pass
        elif "/>" in nug:  #tries to keep out html
          pass
        else:
          urls.add(nugget("PATH", nug)) #a lot of junk is colleted here, ce la vi
    return urls

  def snarf_all(self, nugs):
    all = set()
    for nug in nugs:
      all.add(nugget("WORD", nug))
    return all
    

    

