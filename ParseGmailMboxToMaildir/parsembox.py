from sys import stderr
import argparse
import os
from re import search, sub, IGNORECASE
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
    # Pre-defined date formats
    datefmts = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%d %b %Y %H:%M:%S %z"
    ]

    # extract the key information needed for the output file(s) name and location(s)
    labels = None
    asciidate = None
    padsubj = None
    idHash = None

    for line in bufferArray:
        if search('^X-Gmail-Labels:', line):
            labels = line.split(': ')[1].split(',')
        elif search('^Date:', line):
            mailDate = line.split(': ')[1].split(' (')[0]
            for fmt in datefmts:
                try:
                    asciidate = int(mktime(strptime(mailDate, fmt)))
                except ValueError:
                    pass
        elif search('^Subject:', line):
            rawsubj = line.split('Subject: ')
            if len(rawsubj) == 2:
                padsubj = sub(' ', '_', rawsubj[1])
            else:
                padsubj = '<NO_SUBJECT>'
        elif search('^Message-ID:', line, IGNORECASE):
            idHash = line.split('@')[0].split('<')[1].lower()
            break

    # for each of the labels, create a file and dump out the buffer contents
    if labels and asciidate and padsubj and idHash:
        for label in labels:
            subbed = sub(' ', '_', label)

            try:
                if not os.path.exists(maildirDest + '/' + subbed):
                    os.makedirs(maildirDest + '/' + subbed, 0o755)

                rawfilename = str(asciidate) + '_' + str(padsubj) + '_' + str(idHash) + '.txt'
                emailpath = maildirDest + '/' + subbed + '/' + str(sub('/', '-', rawfilename))
                print(emailpath)

                emailfile = open(emailpath, 'w')
                for line in bufferArray:
                    emailfile.write(str(line) + '\n')
                emailfile.close()

            except PermissionError as e:
                print("Fatal error on creating directory: " + str(e) + "; exiting.")
                exit(1)

# The main brains of the script, the actual runner
if __name__ == '__main__':
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
            if buffering is False and search('^From .*@xxx ', cleaned):
                buffer.append(cleaned)
                buffering = True
            elif buffering is True and not search('^From .*@xxx ', cleaned):
                buffer.append(cleaned)
            elif buffering is True and search('^From .*@xxx ', cleaned):
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
