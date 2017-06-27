import argparse
import os
import re
from time import mktime, strptime

# Setup the parser
#   Takes two compulsory arguments
#   - full path to mbox file
#   - full path to a directory within which the Maildir style spool will be created
#   - Name of the user for the Maildir
parser = argparse.ArgumentParser()
parser.add_argument('mbox', help='Full path to the mbox file.', type=str)
parser.add_argument('dest', help='Full path to output the file structure.', type=str)
parser.add_argument('user', help='Name of the Maildir to be created.', type=str)
args = parser.parse_args()

# Handle each parsed email
def processBuffer(bufferArray, maildirDest):
    timefmt = "%a, %d %b %Y %H:%M:%S %z"

    # extract the key information needed for the output file(s) name and location(s)
    labels = None
    asciidate = None
    padsubj = None
    idHash = None

    for line in bufferArray:
        if re.search('^X-Gmail-Labels:', line):
            labels = line.split(': ')[1].split(',')
        elif re.search('^Date:', line):
            mailDate = line.split(': ')[1]
            asciidate = int(mktime(strptime(mailDate, timefmt)))
        elif re.search('^Subject:', line):
            rawsubj = line.split('Subject: ')[1]
            padsubj = re.sub(' ', '_', rawsubj)
        elif re.search('^Message-ID:', line, re.IGNORECASE):
            idHash = line.split('@')[0].split('<')[1].lower()
            break

    # for each of the labels, create a file and dump out the buffer contents
    if labels and asciidate and padsubj and idHash:
        for label in labels:
            subbed = re.sub(' ', '_', label)

            try:
                if not os.path.exists(maildir + '/' + subbed):
                    os.makedirs(maildir + '/' + subbed, 0o755)

                emailpath = maildir + '/' + subbed + '/' + str(asciidate) + '_' + str(padsubj) + '_' + str(idHash) + '.txt'
                emailfile = open(emailpath, 'w')
                for line in bufferArray:
                    emailfile.write(str(line) + '\n')
                emailfile.close()

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

    # the loop will break out at EOF, but won't process the contents of the last buffer since there is not header for
    # the next email, so the buffer needs to be flushed by calling the process function manually
    processBuffer(buffer, maildir)

    mbox.close()

except FileNotFoundError as e:
    print("Fatal error: " + str(e) + "; exiting.")
    exit(1)

except PermissionError as e:
    print("Fatal error on creating directory: " + str(e) + "; exiting.")
    exit(1)
