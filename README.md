# GSuite
This is a collection of tools for manipulating GSuites services

## ParseGmailMboxToMaildir

This script takes an mbox format file as exported from 
https://takeout.google.com/settings/takeout, and 
  - Parses the file line-by-line, locates the start of each email by header
    - Extracts the text to a buffer
    - Reads the GMail labels for the email
      - Creates a directory hierarchy matching each label
    - Outputs the email as a text file into each directory
