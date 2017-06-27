import argparse
import os
import re
from time import mktime, strptime

# Setup the parser
#   Takes two compulsory arguments
#   - full path to mbox file
#   - full path to a directory within which the Maildir style spool will be created
parser = argparse.ArgumentParser()
parser.add_argument('mbox', help='Full path to the mbox file.', type=str)
parser.add_argument('dest', help='Full path to output the file structure.', type=str)
parser.add_argument('user', help='Name of the Maildir to be created.', type=str)
args = parser.parse_args()

# Handle each parsed email
def processBuffer(bufferArray, maildirDest):
    timefmt = "%a, %d %b %Y %H:%M:%S %z"

    # extract the key information needed for the output file(s) name and location(s)
    for line in bufferArray:
        if re.search('^X-Gmail-Labels:', line):
            labels = line.split(': ')[1].split(',')
            #print(labels)
        elif re.search('^Date:', line):
            mailDate = line.split(': ')[1]
            asciidate = int(mktime(strptime(mailDate, timefmt)))
            #print(asciidate)
        elif re.search('^Message-ID:', line, re.IGNORECASE):
            idHash = line.split('@')[0].split('<')[1].lower()
            #print(idHash)
            break

    for label in labels:
        subbed = re.sub(' ', '_', label)

        try:
            if not os.path.exists(maildir + '/' + subbed):
                os.makedirs(maildir + '/' + subbed, 0o755)

            # email = maildir + '/' + subbed + '/' + asciidate + '_' + idHash + '_'

        except PermissionError as e:
            print("Fatal error on creating directory: " + str(e) + "; exiting.")
            exit(1)

# The main brains of the script, the actual runner
try:
    mbox = open(args.mbox, "r")
    maildir = args.dest + "/" + args.user
    if not os.path.exists(maildir):
        os.makedirs(maildir, 0o755)

    buffer = []
    buffering = False

    rawline = mbox.readline()
    while rawline:
        cleaned = rawline.split('\n')[0]

        # determine what to do with each line read in
        if buffering == False and re.search('^From .*@xxx ', cleaned):
            buffer.append(cleaned)
            buffering = True
        elif buffering == True and not re.search('^From .*@xxx ', cleaned):
            buffer.append(cleaned)
        elif buffering == True and re.search('^From .*@xxx ', cleaned):
            processBuffer(buffer, maildir)
            buffer.clear()
            buffer.append(cleaned)

        rawline = mbox.readline()

    # the loop will always break out before the last contents of the buffer are handled, so needs to be called manually
    processBuffer(buffer, maildir)

    mbox.close()

except FileNotFoundError as e:
    print("Fatal error: " + str(e) + "; exiting.")
    exit(1)

except PermissionError as e:
    print("Fatal error on creating directory: " + str(e) + "; exiting.")
    exit(1)
