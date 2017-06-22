
a = open("/home/vivd/Work/archives/20170426_Wakzi_Katzidziras_archive/Mail/sample.mbox", "r")

while True:
    line = a.readline()
    if not line:
        break
    else:
        print(line)

a.close()