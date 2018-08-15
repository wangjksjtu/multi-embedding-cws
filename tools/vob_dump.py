import cPickle
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument( "--char_vecpath", type = str, default = "char_vec.txt", help = "vector's file")
    parser.add_argument( "--pinyin_vecpath", type = str, default = "pinyin_vec.txt", help = "vector's file")
    parser.add_argument( "--wubi_vecpath",
      type = str,
      default = "wubi_vec.txt",
      help = "vector's file")
    parser.add_argument(
      "--char_dump_path",
      type = str,
      default = "Models/char_dump.pk",
      help = "dump path")
    parser.add_argument(
      "--pinyin_dump_path",
      type = str,
      default = "Models/pinyin_dump.pk",
      help = "dump path")
    parser.add_argument(
      "--wubi_dump_path",
      type = str,
      default = "Models/wubi_dump.pk",
      help = "dump path")

    args = parser.parse_args()

    vob_char = open(args.char_vecpath, 'r')
    lines = vob_char.readlines()
    first_line = lines[0].strip()
    words_num = int(first_line.split()[0])

    vob_char_dict = {}
    for i in xrange(words_num):
        line = lines[i + 1].strip()
        word = line.split()[0].decode("utf-8")
        vob_char_dict[word] = i

    vob_char.close()

    vob_pinyin = open(args.pinyin_vecpath, 'r')
    lines = vob_pinyin.readlines()
    first_line = lines[0].strip()
    pinyin_num = int(first_line.split()[0])

    vob_pinyin_dict = {}
    for i in xrange(pinyin_num):
        line = lines[i + 1].strip()
        pinyin = line.split()[0].decode("utf-8")
        vob_pinyin_dict[pinyin] = i

    vob_pinyin.close()

    vob_wubi = open(args.wubi_vecpath, 'r')
    lines = vob_wubi.readlines()
    first_line = lines[0].strip()
    wubi_num = int(first_line.split()[0])

    vob_wubi_dict = {}
    for i in xrange(wubi_num):
        line = lines[i +1].strip()
        wubi = line.split()[0].decode("utf-8")
        vob_wubi_dict[wubi] = i

    vob_wubi.close()

    with open(args.char_dump_path, 'w') as dop:
        cPickle.dump(vob_char_dict, dop)

    with open(args.pinyin_dump_path, 'w') as dop:
        cPickle.dump(vob_pinyin_dict, dop)

    with open(args.wubi_dump_path, 'w') as dop:
        cPickle.dump(vob_wubi_dict, dop)
