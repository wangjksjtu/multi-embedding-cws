import sys

fo1 = open("character_codelist.txt","r")
fo2 = open("cl_utf8.txt","a")
total_lines = len(fo1.readlines())
lines = 0
fo1.close()
print("Total lines:%d" % total_lines)

fo1 = open("character_codelist.txt","r")

for i in range(6):
    line = fo1.readline()

while 1:
    line = fo1.readline()
    line = line.decode("gbk")
    line = line.encode("utf8")
    fo2.write(line)
    lines = lines + 1
    progress = float(lines) / total_lines * 100.00
    sys.stdout.write("Process progress: %.2f%%      \r" % (progress))
    sys.stdout.flush()

    if not line:
        break

fo1.close()
fo2.close()
