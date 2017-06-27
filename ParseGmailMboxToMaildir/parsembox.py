import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('mbox', help='Full path to the mbox file.', type=str)
parser.add_argument('dest', help='Full path to output the file structure.', type=str)
args = parser.parse_args()

def processBuffer(bufferArray):
    print(len(bufferArray))
    print(str(bufferArray) + "\n\n\n")

try:
    mbox = open(args.mbox, "r")

    buffer = []
    buffering = False

    rawline = mbox.readline()
    while rawline:
        cleaned = rawline.split('\n')[0]

        if buffering == False and re.search('^From .*@xxx ', cleaned):
            buffer.append(cleaned)
            buffering = True
        elif buffering == True and not re.search('^From .*@xxx ', cleaned):
            buffer.append(cleaned)
        elif buffering == True and re.search('^From .*@xxx ', cleaned):
            processBuffer(buffer)
            buffer.clear()
            buffer.append(cleaned)

        rawline = mbox.readline()

    processBuffer(buffer)

    mbox.close()

except FileNotFoundError as e:
    print("Fatal error: " + str(e) + "; exiting.")
    exit(1)
