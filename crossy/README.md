**ip_crossy.py**
============
This script reads the text from files in a directory and stores and visualizes words which are common between the files based on what options the user selects.

**SIMPLE USE EXAMPLES**
----------------------------------
To get an initial understanding of how the script works, consider the following directory:

    test
    ├── file1.txt
    ├── file2.txt
    └── subdirectory
        └── file3.txt
    
with the contents:

- file1.txt:

      email@gmail.com email2@yahoo.com
      123.123.123.3 2607:f0d0:1002:51::4 2607:f0d0:1002:0051:0000:0000:0000:0005
      ether 82:dc:48:e2:a0:01 

- file2.txt:

      this sentence is a nothing sandwich, but not the email email@gmail.com
      or the url https://hello.website.com 2607:f0d0:1002:0051:0000:0000:0000:0004

- file3.txt:

      this sentence is a 123.123.123.003 nothing-burger EB8E09C4-082C-46EB-8210-2C181A92F59C.
      ether 82:dc:48:e2:a0:01
      email@gmail.com
    
To look for common IPs between the 3 files, the command and output would be:

    (base) ---@----- % python ip_crossy.py -p test/ --get_ips
    ********************************************************************************
    IPV6 2607:f0d0:1002:0051:0000:0000:0000:0004:
      test/file2.txt
      test/file1.txt
    IPV4 123.123.123.3:
      test/subdirectory/file3.txt
      test/file1.txt

To look for common emails, the command and output would be:

    (base) ---@----- % python ip_crossy.py -p test/ --yaml sigs.yaml --get_emails 
    ********************************************************************************
    EML_ email@gmail.com:
      test/file2.txt
      test/file1.txt
      subdirectory/file3.txt

_Note the additional argument --yaml sigs.yaml._  This is a file which contains regexes for various patterns of interest, such as emails.  It can be added to as needed, and more than one signature file can be loaded at the same time.  The format of the file will be covered further down.

To look for both common emails and common IPs, the command and output would be:

    (base) ---@----- % python ip_crossy.py -p test --yaml sigs.yaml --get_emails --get_ips
    ********************************************************************************
    IPV4 123.123.123.3:
      test/file1.txt
      test/subdirectory/file3.txt
    EML_ email@gmail.com:
      test/file1.txt
      test/file2.txt
      subdirectory/file3.txt
    IPV6 2607:f0d0:1002:0051:0000:0000:0000:0004:
      test/file1.txt
      test/file2.txt

To see every IPv4, IPv6 and email found, regardless of whether they are common to other files, the command and output would be:

    (base) ---@----- % python ip_crossy.py -p test --yaml sigs.yaml --get_emails --get_ips --print_all
    ********************************************************************************
    EML_ email@gmail.com:
      test/file2.txt
      test/subdirectory/file3.txt
      test/file1.txt
    IPV4 123.123.123.3:
      test/subdirectory/file3.txt
      test/file1.txt
    IPV6 2607:f0d0:1002:0051:0000:0000:0000:0004:
      test/file2.txt
      test/file1.txt
    EML_ email2@yahoo.com:
      test/file1.txt
    IPV6 2607:f0d0:1002:0051:0000:0000:0000:0005:
      test/file1.txt

With the usage examples above in mind, here are all the options the script provides:

    usage: ip_crossy.py [-h] [--path [PATH [PATH ...]]] [--get_ips] [--get_urls]
                        [--get_emails] [--get_phones] [--get_financial]
                        [--get_misc] [--get_all] [--verbose] [--neo4j] [--csv]
                        [--tagged] [--print_all] [--exts [EXTS [EXTS ...]]]
                        [--yaml [YAML [YAML ...]]]

    reads text from files and looks for common strings between them; looks for
    email/jabber/telegram, ipv4/6, and ... strings

    optional arguments:
      -h, --help            show this help message and exit
      --path [PATH [PATH ...]], -p [PATH [PATH ...]]
                            input file or directory
      --get_ips             parse for IPv4 and IPv6
      --get_urls            parse for url-ish strings
      --get_emails          parse for email-ish strings
      --get_phones          parse for phone numbers
      --get_financial       parse for credit cards, btc addresses
      --get_misc            parse for other stuff (e.g. lat,long; MAC address; )
      --get_all, -a         store every word found
      --verbose, -v         prints much more to the screen; e.g. which files are
                            skipped in a directory
      --neo4j               put data into a neo4j database for visualization
      --csv                 print data as csv
      --tagged              only look at files that start with '_N_'
      --print_all           print every nugget found
      --exts [EXTS [EXTS ...]]
                            only look at files with these extensions
      --yaml [YAML [YAML ...]], -y [YAML [YAML ...]]
                            load a yaml signature file

**FILE TYPES THE SCRIPT SKIPS**
-------------------------------------------

The file **skipexts.txt** contains some extensions which this script is not suitable to read from and which should be skipped.  Here are the contents of the file as of 2021-04-30:

    #ADOBE
      .pdf
    #OFFICE
      .doc .docx
      .ppt .pptx
      .xls .xlsx
    #GRAPHICS
      .bmp
      .jpg .jpeg .jpe .jif .jfif .jfi
      .png
      .psd
      .gif
      .tif .tiff
      .webp
    #COMPRESSION
      .gz .tar .zip
    #SOUND
      .wav .mp3
    #OTHER NO-GO's
      .dmg .sks

Lines that begin with pound sign (#) are skipped entirely and are used for notes.  They have no impact on how the program runs.  Add new extensions as needed, using the format as shown.

**YAML SIGNATURE FILES**
----------------------------------

The stock file provided is named **sigs.yaml**, but any number of files can be provided to the script via --yaml <file name> arguments.  There are two categories of searches which the yaml signature file can conduct: _string_ and _pattern_.  Two example signatures are provided below to show how to use this functionality for each category.

**STRING SEARCHES:**

The following yaml signature will look through every document in the search directories for the string "gmail":

    str_gmail:
      description: Finds the string >gmail<
      string: gmail
      case_sensitive: False

Line-by-line, here is how the signature works.  **ALL KEYS (the words to the left of the colon (:) ) MUST BE UNCHANGED AND PRESENT FOR YOUR YAML SIGNATURE TO WORK.**

    str_gmail: << this value can be anything; it should describe what you're searching for.  It will show up as a "Node Label" if you push the data into neo4j (discussed further down).

      description: anything can go here; use this field to describe what the yaml sig is supposed to do...

      string: << any string you wish to search for can go in the place of "gmail" above; add as many different stings as you like by copy/pasta of the entire yaml block above.

      case_sensitive: False << can be either "True" or "False"; If True, then the search will be case sensitive.

**PATTERN SEARCHES:**

    FON1:
      description: Phone number regex
      args_tiein: get_phones
      regex: ^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$
  
As with string searches, the keys must be kept exactly as shown in the block above.  Line-by-line, here is how the signature works:

    FON1: << this value can be anything, as for the string search.  Short values work nicely due to how neo4j visualizes the data.
             
      description: << same as above.
      
      args_tiein: << This is complex and will be skipped for now.
      
      regex: << the regex goes here.  The script reads the value as a raw string so there is no need to escape backslashes.
            
The **args_tiein** key is used to link yaml signature patterns to the following command line arguments:

      --get_urls            parse for url-ish strings
      --get_emails          parse for email-ish strings
      --get_phones          parse for phone numbers
      --get_financial       parse for credit cards, btc addresses
      --get_misc            parse for other stuff (e.g. lat,long; MAC address; )

In the yaml block **FON1** above, the line **args_tiein: get_phones** ties the yaml signature to the command line argument **--get_phones**.  I.e., if the user adds the --get_phones flag to their search, then the yaml signature will execute and the regex will be searched.  If the --get_phones flag is not included, then this yaml signature will not be searched.

If you add a new yaml pattern search, you must tie it to a command line argument, or the yaml signature will never get searched.  If in doubt, just use the following:
  
      args_tiein: get_misc

and make sure to execute the script with the **--get_misc** flag.


**NEO4J**
------------

Neo4j is a graph database which can be used to visualize the data this script finds.  An example bloom graph is included in the file **README_neo4j_example.png**.  This graph was created using the data from file1.txt, file2.txt and file3.txt. 

To install Neo4j, go to **neo4j.com** and follow the instructions.  You will have to create an account there to get the software key required for a desktop version of the program.  Once neo4j is installed, make sure it is running on your local machine and that a database instance is created.  _This script will push data into whatever database instance is running at that time, so be careful!_  The operation of neo4j is outside the scope of this readme, but below are two commands I found very useful when starting out:

* To start over (this will delete everything in the active database):

      MATCH (n) DETACH DELETE n

* To view all nodes with > 1 connection:

      MATCH ()-[r]->(n)
      WITH n, count(r) as rel_cnt
      WHERE rel_cnt > 1
      RETURN ()-[]->(n)

To get to the bloom functionality, click on "Neo4j Bloom" on the left side of the main Neo4j desktop window (circa 2021-04-30).
