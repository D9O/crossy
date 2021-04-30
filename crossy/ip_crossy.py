import os
import sys
import yaml
import pprint
import argparse

#home-baked imports:
from lafienc import laboriously_find_encoding
from snarfy import snarf
from neo4j_secretary import n4j

#this traverses directories and selects files for loading based on the command
#line args provided by the user
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
        if verbose:
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
        # THIS IS WHERE CONTROL GOES TO SNARFY.PY AND THE WORK IS BEGUN
        snf.file(path, safe_enc, args)

#this gets a list of files in a directory
def get_all_files(path):
  paths = set()
  for root, dirs, files in os.walk(path):
    for f in files:
      paths.add(os.path.join(root, f))
  return(paths)

if __name__=="__main__":
  parser = argparse.ArgumentParser(description="reads text from files and looks for common strings between them; tags for emails, telephone numbers, GUIDs, ipv4/6, and strings; customize your pattern searches via yaml signatures (see README.md)")
  parser.add_argument("--path", "-p", help="input file or directory", nargs="*", action="append")
  parser.add_argument("--get_ips", help="parse for IPv4 and IPv6", action="store_true")
  parser.add_argument("--get_urls", help="parse for url-ish strings", action="store_true")
  parser.add_argument("--get_emails", help="parse for email-ish strings", action="store_true")
  parser.add_argument("--get_phones", help="parse for phone numbers", action="store_true")
  parser.add_argument("--get_financial", help="parse for credit cards, btc addresses", action="store_true")
  parser.add_argument("--get_misc", help="parse for other stuff (e.g. lat,long; MAC address; )", action="store_true")
  parser.add_argument("--get_all", "-a", help="store every word found", action="store_true")
  parser.add_argument("--verbose", "-v", help="prints much more to the screen; e.g. which files are skipped in a directory", action="store_true")
  parser.add_argument("--neo4j", help="put data into a neo4j database for visualization", action="store_true")
  parser.add_argument("--csv", help="print data as csv", action="store_true")
  parser.add_argument("--tagged", help="only look at files that start with '_N_'", action="store_true")
  parser.add_argument("--print_all", help="print every nugget found", action="store_true")
  parser.add_argument("--exts", help="only look at files with these extensions", nargs="*", action="append")
  parser.add_argument("--yaml", "-y", help="load a yaml signature file",
    nargs="*", action="append")
  args = parser.parse_args()
  verbose = args.verbose
  tagged = args.tagged
  
  #anything other than ipv4 and ipv6 requires a yaml signature, this
  #checks that this requirement is met.
  if (args.get_urls or args.get_emails or args.get_phones or args.get_financial or args.get_misc):
    if args.yaml == None:
      sys.exit("No signature file was provided.  Without the signature file, all I can look for is IPv4 and IPv6.  The default signature files is sigs.yaml")
  
  #this gathers command-line provided file extensions the user provided
  #that should be read (e.g. if the user only wanted to look at .csv and .txt
  #files in a directory)
  exts = set()
  if args.exts != None:
    for ext_list in args.exts:
      exts |= set(ext_list)

  #this initializes snarfy.py to run; snarfy.py does the work of finding stings
  #patterns and matches between documents.
  snf = snarf(args.print_all, args.yaml)
  #this finds a safe encoding to open a file with.  It is ugly, but works.
  lfe = laboriously_find_encoding(verbose)
  
  #this creates the set of all the files in a directory
  file_set = set()
  for file_list in args.path:
    for local_path in file_list:
      if os.path.isfile(local_path):
        file_set.add(local_path)
      elif os.path.isdir(local_path):
        file_set |= get_all_files(local_path)
  
  #this goes through each file found above, and if it's something the user
  #wants to look at, it is scraped for data via snarfy.py
  for file in file_set:
    file_look(file)

  #if the user wants csv output for an excel pivot table, this does it.
  if args.csv:
    print(snf.csv())
  #otherwise, a "normal" printout of the results is created
  else:
    print(f"{snf}")
  
  #if the user wants to push data into neo4j for visualization, this does that.
  if args.neo4j:
    n = n4j(snf, verbose)
    n.store()

  #the end.

