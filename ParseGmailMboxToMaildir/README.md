# ParseGmailMboxToMaildir #

## Description ##
This script takes an mbox format file as exported from 
https://takeout.google.com/settings/takeout, and 
  - Parses the file line-by-line, locates the start of each email by header
    - Extracts the text to a buffer
    - Reads the GMail labels for the email
      - Creates a directory hierarchy matching each label
    - Outputs the email as a text file into each directory

## Disclaimer ##

__THIS HAS ONLY BEEN TESTED ON WINDOWS 10 AND UBUNTU LINUX, ON MBOX FILES GENERATED
BY DATA EXPORTS FROM GOOGLE ONLY. AND IT WORKS; THIS DOESN'T MEAN IT WILL WORK FOR 
YOU, (SORRY IF IT DOESN'T) AND I TAKE NO RESPONSIBILITY FOR ANYTHING GOING WRONG.__

__SO, BACKUP EVERYTHING - MULTIPLE TIMES - AND TEST, TEST, TEST AND TEST AGAIN BEFORE 
USING IN PRODUCTION.__

## Assumptions & Limitations ##

  - Python version: 3.5.2 amd64 on Windows 10 and Ubuntu 16.04 Linux; _should_ 
  work with any other version of Python 3 as no non-standard libraries used
  - Google outputs the mbox in DOS-style with CRLF line terminators, so the 
  _read_ operation on the mbox file is done with an explicit '__\r\n__' line 
  terminator defined  
  - Windows paths need to be written with forward slashes; for example 
  _C:\Users\username\folder_ should be written as _C:/Users/username/folder_ 
  - Due to Windows having limits on the length of file path and name, full paths 
  are truncated at 135 characters (+ 3 characters for '...' and another 4 
  characters for '.txt' extension) if necessary
  - Forced encoding to UTF-8 for file reading and writing, otherwise Windows uses 
  _charmap_ encoding and fails out on some characters seen as illegal and / or 
  not recognised
  - Handles only two date formats at the moment, might need to extend this to 
  suit any other combinations
  - Common characters illegal in filename in Windows and Linux are stripped out, 
  but the list might not be complete  

## Usage ##
```
$ python3 /path/to/parsembox.py /path/to/mbox_file.mbox /path/to/Maildir <MAILDIR_NAME>
```

## Output format and paths ##
```
/path/to/Maildir/<MAILDIR_NAME>/<LABELS_DIRS>/<EPOCH_DATE>_<THREAD_ID>_<EMAIL_SUBJECT>.txt
```