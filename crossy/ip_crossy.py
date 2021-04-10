import os
import sys
import yaml # $pip3 install pyyaml
import pprint
import argparse

#home-baked imports:
from lafienc import laboriously_find_encoding
from snarfy import snarf
from neo4j_secretary import n4j

def file_look(path):
  global verbose
  global recursive
  global tagged
  global exts
  global snf
  global lfe
  if os.path.isfile(path):
    snarf_file = True
    if len(exts) > 0:
      if os.path.splitext(path)[1] not in exts:
        snarf_file = False
        print(f"  {os.path.basename(path)} extension not in the list you provided; skipping")
    if tagged:
      if os.path.basename(path)[:3] != "_N_":
        snarf_file = False
        if verbose:
          print(f"  {os.path.basename(path)} does not start with _N_; skipping")
    if snarf_file:
      if verbose:
        print(f"  searching in file {path}", end = "")
      safe_enc = lfe.get_safe_enc(path)
      if safe_enc != None:
        snf.file(path, safe_enc, args)

def get_all_files(path):
  paths = set()
  for root, dirs, files in os.walk(path):
    for f in files:
      paths.add(os.path.join(root, f))
  return(paths)

if __name__=="__main__":
  parser = argparse.ArgumentParser(description="reads text from files and looks for common strings between them; looks for email/jabber/telegram, ipv4/6, and ... strings")
  parser.add_argument("--path", "-p", help="input file or directory", nargs="*", action="append")
  parser.add_argument("--get_ips", "-i", help="parse for IPv4 and IPv6", action="store_true")
  parser.add_argument("--get_paths", "-g", help="parse for file path-ish strings", action="store_true")
  parser.add_argument("--get_emails", "-e", help="parse for email-ish strings", action="store_true")
  parser.add_argument("--get_all", "-a", help="store every word found", action="store_true")
  parser.add_argument("--verbose", "-v", help="prints much more to the screen; e.g. which files are skipped in a directory", action="store_true")
  parser.add_argument("--neo4j", help="put data into a neo4j database for visualization", action="store_true")
  parser.add_argument("--csv", help="print data as csv", action="store_true")
  parser.add_argument("--tagged", help="only look at files that start with '_N_'", action="store_true")
  parser.add_argument("--print_all", help="print every nugget found", action="store_true")
  parser.add_argument("--exts", help="only look at files with these extensions", nargs="*", action="append")
  args = parser.parse_args()
  verbose = args.verbose
  tagged = args.tagged
  
  exts = set()
  if args.exts != None:
    for ext_list in args.exts:
      exts |= set(ext_list)

  snf = snarf(args.print_all)
  lfe = laboriously_find_encoding(verbose)
  
  file_set = set()
  for file_list in args.path:
    for local_path in file_list:
      if os.path.isfile(local_path):
        file_set.add(local_path)
      elif os.path.isdir(local_path):
        file_set |= get_all_files(local_path)
  
  for file in file_set:
    file_look(file)

  if args.csv:
    print(snf.csv())
  else:
    print(f"{snf}")
  
  if args.neo4j:
    n = n4j(snf, verbose)
    n.store()

'''
This query in neo4j will show all the nuggets with > 1 connection:
MATCH ()-[r]->(n)
WITH n, count(r) as rel_cnt
WHERE rel_cnt > 1
RETURN ()-[]->(n)
'''

