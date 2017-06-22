
a = open("/home/vivd/Work/archives/wk/Mail/sample.mbox", "r")

while True:
    line = a.readline()
    if not line:
        break
    else:
        print(line)

a.close()