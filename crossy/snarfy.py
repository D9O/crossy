import ipaddress
import yaml
import re
import colorama
from colorama import Fore, Back, Style
colorama.init()
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL
#
#######################################################################

from pynugget import nugget

#this class reads through each word in a document creates a tagged "nugget" of
#data, per the user's command line arguments (e.g. it will find IPs, or emails,
#or btc addresses).
class snarf:
  def __init__(self, print_arg, yaml_files):
    self.print_all = print_arg
    #the below loads the yaml signatures:
    self.yaml_sigs = {"regexes": [], "strings": []}
    if yaml_files != None:
      for file_list in yaml_files:
        for f in file_list:
          file_contents = []
          if f != None:
            with open(f, "r") as orf:
              file_contents.append(yaml.load(orf, Loader=yaml.FullLoader))
          #the below splits the yaml signatures into the two categories of
          #string searches and regex pattern searches
          for rule in file_contents:
            for rule_name, rule_details in rule.items():
              if "regex" not in rule_details.keys():
                self.yaml_sigs["strings"].append({rule_name: rule_details})
              else:
                self.yaml_sigs["regexes"].append({"rule_name": rule_name,
                                                  "regex": re.compile(r"{}".format(rule_details["regex"])),
                                                  "args_tiein": rule_details["args_tiein"]})
            
    self.nug2doc = {} #all the data snarfed up goes into here and ...
    self.doc2nug = {} #here.
  
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
  
  #print for use in an Excel pivot table
  def csv(self):
    output = '\n\n"TYPE","VALUE","FILE"\n'
    for nugget, docs in self.nug2doc.items():
      if self.print_all or len(docs) > 1:
        for doc in docs:
          output += f'{nugget.csv()},"{doc}"\n'
    return output

  #open a file with a safe encoding
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
      
  #this is where words (nuggets) are tagged as email, ipv4, ipv6, etc etc
  def process_row(self, row, args):
    snarfed = set()
    if len(self.yaml_sigs) > 0:
      snarfed |= self.snarf_yaml(row, args)
    if args.get_ips or args.get_all:
      raw_nuggets = self.make_nuggets(row)
      if args.get_ips:
        snarfed |= self.snarf_ips(raw_nuggets)
      if args.get_all:
        snarfed |= self.snarf_all(raw_nuggets)
    return snarfed
 
  #make_nuggets takes a string and chops it into words (which I call "nuggets").
  def make_nuggets(self, row):
    nugget_set = set()
    row = row.strip()
    #this gets rid of common escape sequences (e.g. annoying bell dings, do not
    #remove this Andy!)
    #thank you to: hxxps://stackoverflow.com/questions/8115261/how-to-remove-all-the-escape-sequences-from-a-list-of-strings
    escapes = "".join([chr(char) for char in range(1, 32)])
    translator = str.maketrans("", "", escapes)
    row = row.translate(translator)
    for c in ",!$%&*(){}[]<>?;|\`\"'\t": #split on all of these
      row = row.replace(c, " ")
    nugs = set([n for n in row.split(" ") if len(n)>0])
    end_cl = ".:;,!?-=" #clean endings so that "word." is the same as "word"
    for nug in nugs:
      if nug[-1] in end_cl:
        nug = nug[:-1]
      if len(nug) > 1:
        nugget_set.add(nug)
    return(nugget_set)

  #this identifies IPs amongst the nuggets.  Doing it this way is worth the
  #overhead because it works better than regex, in my own experience.
  def snarf_ips(self, nugs):
    ips = set()
    for nug in nugs:
      try:
        ip = ipaddress.ip_address(nug)
        if ip.is_loopback:              #these IPs not what I'm looking for...
          continue
        
        elif ip.version == 6:
          ips.add(nugget("IPV6", ip.exploded))
        elif ip.version == 4:
          ips.add(nugget("IPV4", ip.exploded))
      except:
        continue
    return ips

  #if you want to create a graph of every word in each document, this
  #is the part that does it.
  def snarf_all(self, nugs):
    all = set()
    for nug in nugs:
      all.add(nugget("WORD", nug))
    return all
  
  #this determines which yaml signatures to run, based on the command line
  #arguments the user provided
  def snarf_yaml(self, row, args):
    #this part handles pattern searches
    return_val = set()
    for rule in self.yaml_sigs["regexes"]:
      if f"{rule['args_tiein']}=True" in f"{args}": #very hacky, but it works
        hits = rule["regex"].finditer(row)
        if hits == None:
          continue
        for hit in hits:
          return_val.add(nugget(rule["rule_name"], hit.group()))
    #this part handles string searches
    for rule in self.yaml_sigs["strings"]:
      for rule_name, rule_details in rule.items():
        if rule_details["case_sensitive"] == False:
          if rule_details["string"].lower() in row.lower():
            return_val.add(nugget(rule_name, rule_details["string"]))
        elif rule_details["string"] in row:
          return_val.add(nugget(rule_name, rule_details["string"]))
    return return_val
    

