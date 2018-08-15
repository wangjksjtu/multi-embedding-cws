from pypinyin import lazy_pinyin
import sys,time

fo1 = open("pre_chars_for_w2v.txt", "r")
fo2 = open("pre_pinyin_for_w2v.txt", "a")

total_lines = len(fo1.readlines())
print("Total lines: %d" % (total_lines))
fo1.close()
lines = 0

fo1 = open("pre_chars_for_w2v.txt", "r")

while 1:
    line = fo1.readline()
    line = line.decode("utf8")
    pinyinset = lazy_pinyin(line)
    lines = lines + 1
    progress = (float(lines) / total_lines) * 100.00
    sys.stdout.write("Process progress: %.2f%%    \r" % (progress))
    sys.stdout.flush()

    for pinyin in pinyinset:
        pinyin = pinyin.encode("utf8")
        fo2.write(pinyin)

    if not line:
        break

fo1.close()
fo2.close()