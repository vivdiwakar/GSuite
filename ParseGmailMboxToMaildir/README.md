# ParseGmailMboxToMaildir #

## Description ##
This script takes an mbox format file as exported from 
https://takeout.google.com/settings/takeout, and 
  - Parses the file line-by-line, locates the start of each email by header
    - Extracts the text to a buffer
    - Reads the GMail labels for the email
      - Creates a directory hierarchy matching each label
    - Outputs the email as a text file into each directory

## Usage ##
```
$ python3 /path/to/parsembox.py /path/to/mbox_file.mbox /path/to/Maildir
```

## Fixes ##
  - Handle the case where the destination Maildir already exists  