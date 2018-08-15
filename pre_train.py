# -*- coding: utf-8 -*-

import SentHandler as snhd
import argparse

def main(corpusAll,
         char_vecpath,
         pinyin_vecpath,
         wubi_vecpath,
         train_file,
         test_file,
         test_file_raw,
         test_file_gold,
         MAX_LEN,
         test_size,
         step):

    vob = open(char_vecpath, 'r')
    lines = vob.readlines()
    first_line = lines[0].strip()
    words_num = int(first_line.split()[0])

    vob_dict = {}
    for i in xrange(words_num):
        line = lines[i + 1].strip()
        word = line.split()[0].decode("utf-8")
        vob_dict[word] = i

    vob.close()

    pinyin = open(pinyin_vecpath, 'r')
    lines = pinyin.readlines()
    first_line = lines[0].strip()
    words_num = int(first_line.split()[0])

    pinyin_dict = {}
    for i in xrange(words_num):
        line = lines[i + 1].strip()
        word = line.split()[0].decode("utf-8")
        pinyin_dict[word] = i

    pinyin.close()

    wubi = open(wubi_vecpath, 'r')
    lines = wubi.readlines()
    first_line = lines[0].strip()
    words_num = int(first_line.split()[0])

    wubi_dict = {}
    for i in xrange(words_num):
        line = lines[i + 1].strip()
        word = line.split()[0]
        wubi_dict[word] = i

    wubi.close()

    fo1 = open("Encode/cl_utf8.txt", "r")
    dic_wubi = dict()

    while 1:
      line = fo1.readline()
      if not line:
        break
      line = line.split()
      word = line[0]
      wubi = line[2]
      dic_wubi[word] = wubi

    fo1.close()

    inp = open(corpusAll, 'r')
    bad_lines = 0
    cnt = 0

    trop_ = open(train_file+"train_char.txt", 'w')
    ttop_ = open(test_file+"test_char.txt", 'w')
    trop_pinyin_ = open(train_file + "train_pinyin.txt", "w")
    ttop_pinyin_ = open(test_file + "test_pinyin.txt", "w")
    trop_wubi_ = open(train_file + "train_wubi.txt", "w")
    ttop_wubi_ = open(test_file + "test_wubi.txt", "w")
    ttrop_ = open(test_file_raw, 'w')
    ttgop_ = open(test_file_gold, 'w')
    with trop_ as trop, ttop_ as ttop, trop_pinyin_ as trop_pinyin, ttop_pinyin_ as ttop_pinyin, trop_wubi_ as trop_wubi, ttop_wubi_ as ttop_wubi, ttrop_ as ttrop, ttgop_ as ttgop:
        for ind, line in enumerate(inp):
            line_pieces = []
            NE_free_line = snhd.NE_Removing(line)
            flag = snhd.SliceSentence(NE_free_line, line_pieces, [], tag = True, max_len = MAX_LEN)

            if not flag:
                bad_lines += 1
                continue

            analyzed_pieces,analyzed_pieces_pinyin, analyzed_pieces_wubi, flag = snhd.Analyze(line_pieces, vob_dict, pinyin_dict, wubi_dict, dic_wubi, max_len = MAX_LEN)


            if not flag:
                bad_lines += 1
                continue

            if (ind + 1) % step == 0 and cnt < test_size :
                for piece_raw, piece in zip(line_pieces, analyzed_pieces):
                    ttrop.write(snhd.CleanSentence(piece_raw, set([])))
                    ttgop.write(snhd.CleanSentence(piece_raw, set([]), interval = u' '))
                    ttop.write(piece)
                for piece_raw, piece in zip(line_pieces, analyzed_pieces_pinyin):
                    ttop_pinyin.write(piece)
                for piece_raw, piece in zip(line_pieces, analyzed_pieces_wubi):
                    ttop_wubi.write(piece)
                cnt += 1

            else:
                for piece in analyzed_pieces:
                    trop.write(piece)
                for piece in analyzed_pieces_pinyin:
                    trop_pinyin.write(piece)
                for piece in analyzed_pieces_wubi:
                    trop_wubi.write(piece)

        print "Generating finished, gave up %d bad lines" % bad_lines

    inp.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
      "--corpusAll",
      type = str,
      default = "Corpora/people2014All.txt",
      help = "corpus file")
    parser.add_argument(
      "--char_vecpath",
      type = str,
      default = "char_vec.txt",
      help = "char_vector's file")
    parser.add_argument(
      "--pinyin_vecpath",
      type = str,
      default = "pinyin_vec.txt",
      help = "pinyin_vector's file")
    parser.add_argument(
      "--wubi_vecpath",
      type = str,
      default = "wubi_vec.txt",
      help = "wubi_vector's file")
    parser.add_argument(
      "--train_file",
      type = str,
      default = "Corpora/",
      help = "training file will be generated here")
    parser.add_argument(
      "--test_file",
      type = str,
      default = "Corpora/",
      help = "testing file will be generated here")
    parser.add_argument(
      "--test_file_raw",
      type = str,
      default = "Corpora/test_raw.txt",
      help = "testing raw file will be generated here")
    parser.add_argument(
      "--test_file_gold",
      type = str,
      default = "Corpora/test_gold.txt",
      help = "gold file will be generated here")

    parser.add_argument(
      "--MAX_LEN",
      type = int,
      default = 80,
      help = "max sentencen length")
    parser.add_argument(
      "--test_size",
      type = int,
      default = 8000,
      help = "the sentence lines of testing file")
    parser.add_argument(
      "--step",
      type = int,
      default = 50,
      help = "program chooses 1 test sentence for every <step> steps")

    args = parser.parse_args()
    main(args.corpusAll, args.char_vecpath, args.pinyin_vecpath, args.wubi_vecpath, args.train_file,
        args.test_file, args.test_file_raw, args.test_file_gold,
        args.MAX_LEN, args.test_size, args.step)
