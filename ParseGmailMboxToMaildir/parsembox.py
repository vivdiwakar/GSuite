import argparse
import os
from re import search, sub, escape
from time import mktime, strptime

# Setup the parser
parser = argparse.ArgumentParser()
parser.add_argument('mbox', help='Full path to the mbox file.', type=str)
parser.add_argument('dest', help='Full path to output the newly parsed Maildir.', type=str)
parser.add_argument('user', help='Name of the Maildir to be created, usually "Maildir".', type=str)
args = parser.parse_args()

# Handle each parsed email
def processBuffer(bufferArray, maildirDest):
    # Pre-defined date formats to handle
    # This might need to be tweaked in future
    datefmts = ["%a, %d %b %Y %H:%M:%S %z", "%d %b %Y %H:%M:%S %z"]
    # Illegal characters that Windows can't handle for paths and file names
    illegalchars = ['!', '?', '<', '>', ':', '"', '/', '\\', '*', '~', '#', '%', '&', '[', ']', '(', ')', '{', '}',
                    '|', '@', ' ', '\'', '.']
    # Windows has file path + name limits, limiting to 135 characters + '...' filler (3 chars) + '.txt' file
    # extension (4 chars)
    WindowsMaxPathLen = 135
    labels = None
    asciidate = None
    padsubj = None
    threadID = None

    # extract the key information needed for the output file(s) name and location(s)
    for index, line in enumerate(bufferArray):
        if search('^X-Gmail-Labels:', line):
            mlLabel = line
            index += 1
            try:
                while not search('^.*:', bufferArray[index]):
                    mlLabel += str(bufferArray[index])
                    index += 1
            except IndexError:
                pass
            stripped = sub('"', '', str(mlLabel))
            labels = str(stripped).split(': ')[1].split(',')
        elif search('^X-GM-THRID:', line):
            threadID = line.split(': ')[1]
        elif search('^Date: ', line):
            mailDate = line.split(': ')[1].split(' (')[0]
            for fmt in datefmts:
                try:
                    asciidate = int(mktime(strptime(mailDate, fmt)))
                except ValueError:
                    pass
        elif search('^Subject:', line):
            rawsubj = line.split('Subject: ')
            if len(rawsubj) == 2:
                padsubj = (rawsubj[1][:WindowsMaxPathLen] + '...') \
                    if len(rawsubj[1]) > (WindowsMaxPathLen + 3) else rawsubj[1]
            else:
                padsubj = '<NO_SUBJECT>'
            break

    # for each of the labels, create a file and dump out the buffer contents
    if labels and asciidate and padsubj and threadID:
        for label in labels:
            subbed = sub(' ', '_', label.lstrip().rstrip())

            try:
                if not os.path.exists(maildirDest + '/' + subbed):
                    os.makedirs(maildirDest + '/' + subbed, 0o755)

                rawfilename = str(asciidate) + '_' + str(threadID) + '_' + str(padsubj)
                strippedfilename = sub(u'(?u)[' + escape(''.join(illegalchars)) + ']', '_', rawfilename)
                emailpath = maildirDest + '/' + subbed + '/' + str(sub('/', '-', strippedfilename)) + '.txt'

                emailfile = open(emailpath, mode='w', encoding="utf8")
                for line in bufferArray:
                    emailfile.write(str(line + '\n'))
                emailfile.close()

            except PermissionError as e:
                print("Fatal error: " + str(e) + "; exiting.")
                exit(1)

# The main brains of the script, the actual runner
if __name__ == '__main__':
    try:
        buffer = []
        buffering = False

        maildir = args.dest + "/" + args.user
        if not os.path.exists(maildir):
            os.makedirs(maildir, 0o755)

        # Google returns the mbox file with DOS-style with CRLF line terminators, so needs to be defined here
        mbox = open(args.mbox, mode="r", encoding="utf8", newline='\r\n')
        rawline = mbox.readline()
        while rawline:
            cleaned = rawline.strip()

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

        # the loop will break out at EOF, but won't process the contents of the last buffer since there is not header
        # for the next email, so the buffer needs to be flushed by calling the process function manually
        processBuffer(buffer, maildir)

        mbox.close()

    except [ FileNotFoundError, PermissionError, OSError ] as e:
        print("Fatal error: " + str(e) + "; exiting.")
        exit(1)
