# -*- coding: utf-8 -*-

# import pdb
from pypinyin import lazy_pinyin

# NOTE the sequence of elements in this list, they have different prority.
STOP = [u'。', u'？', u'！', u'?', u'!', u'：', u'；', u';', u'…', u'，', u',', u'、']

# default max length of sentence
MAX_LEN = 100

# BMES
# 0-> 'S'
# 1-> 'B'
# 2-> 'M'
# 3-> 'E'
TAGS = [0, 1, 2, 3]


# find the index of a particular symbol in line, line can be 'str' or 'list'
def FindIndex(line, symbol):
	if type(line) == unicode:
		return line.find(symbol)
	else:
		ind = -1
		for i in xrange(len(line)):
			if line[i][0] == symbol:
				ind = i
				break

		return ind

# get the length of a line according to its type
def GetLength(line):
	if type(line) == unicode:
		return len(line)
	else:
		length = 0
		for token in line:
			index = token[::-1].find(u'/') + 1
			length += len(token) - index

		return length

# write a line, depends on its type
def WriteLine(line, out_list):
	if type(line) == unicode:
		out_list.append(line.encode("utf-8") + '\n')
	else:
		newline = u' '.join(line)
		out_list.append(newline.encode("utf-8") + '\n')


# Slicing a sentence like a binary tree
def BiTreeSlicing(ustr, cnt, symbols, start, out_list):
	if start == len(STOP) - 1:
		return False, cnt

	ind = 0
	newstart = 0

	for i in xrange(start, len(symbols)):
		ind = FindIndex(ustr, symbols[i]) + 1
		if ind > 1:
			newstart = i + 1
			break

	if ind == 0:
		return False, cnt

	f1 = True
	f2 = True
	left = ustr[ : ind]
	left_len = GetLength(left)
	right = ustr[ind : ]
	right_len = GetLength(right)

	if left_len > MAX_LEN - 1:
		f1, cnt = BiTreeSlicing(left, cnt, STOP, newstart, out_list)
	elif left_len > 0:
		WriteLine(left, out_list)
		cnt += 1

	if right_len > MAX_LEN:
		f2, cnt = BiTreeSlicing(right, cnt, STOP, start, out_list)
	elif right_len > 0:
		WriteLine(right, out_list)
		cnt += 1

	flag = f1 and f2
	return flag, cnt

def SliceSentence(line, out_list, cut_count, tag = False, max_len = 100):
	if len(line) == 0:
		return False

	global MAX_LEN
	MAX_LEN = max_len

	ustr = line.decode("utf-8")
	ustr = ustr.strip()
	if tag:
		ustr = ustr.split()

	cnt = 1
	length = GetLength(ustr)
	if length < 3:
		return False

	flag = True
	if length > MAX_LEN:
		cnt = 0
		try:
			flag, cnt = BiTreeSlicing(ustr, cnt, STOP, 0, out_list)
		except Exception as e:
			print e
			return False

	else:
		WriteLine(ustr, out_list)

	cut_count.append(cnt)
	return flag

# labeling
def Analyze(pieces, vob_dict, pinyin_dict, wubi_dict, dic_wubi, max_len = 100):
	global MAX_LEN
	MAX_LEN = max_len

	new_pieces = []
	new_pieces_pinyin = []
	new_pieces_wubi = []
	for piece in pieces:
		ustr = piece.decode("utf-8").strip()
		lst = ustr.split()

		X = []
		X_pinyin = []
		X_wubi = []
		Y = []

		for token in lst:
			index = token[::-1].find(u'/') + 1
			word = token[ : (len(token) - index)]
			leng = len(word)
			if leng > 1:
				for j, char in enumerate(word):
					char_pinyin = lazy_pinyin(char)[0]

					if dic_wubi.has_key(char.encode("utf8")):
						char_wubi = dic_wubi[char.encode("utf8")]
					else:
						char_wubi = char.encode("utf8")


					if vob_dict.has_key(char):
						X.append(vob_dict[char])
					else:
						X.append(vob_dict[u"<UNK>"])

					if pinyin_dict.has_key(char_pinyin):
						X_pinyin.append(pinyin_dict[char_pinyin])
					else:
						X_pinyin.append(pinyin_dict[u"<UNK>"])

					if wubi_dict.has_key(char_wubi):
						X_wubi.append(wubi_dict[char_wubi])
					else:
						X_wubi.append(wubi_dict["<UNK>"])

					if j == 0:
						Y.append(TAGS[1])
					elif j == leng - 1:
						Y.append(TAGS[3])
					else:
						Y.append(TAGS[2])
			else:
				if word=='':
					word_pinyin=''
				else:
					word_pinyin = lazy_pinyin(word)[0]

				if dic_wubi.has_key(word.encode("utf8")):
					word_wubi = dic_wubi[word.encode("utf8")]
				else:
					word_wubi = word.encode("utf8")


				if vob_dict.has_key(word):
					X.append(vob_dict[word])
				else:
					X.append(vob_dict[u"<UNK>"])

				if pinyin_dict.has_key(word_pinyin):
					X_pinyin.append(pinyin_dict[word_pinyin])
				else:
					X_pinyin.append(pinyin_dict[u"<UNK>"])

				if wubi_dict.has_key(word_wubi):
					X_wubi.append(wubi_dict[word_wubi])
				else:
					X_wubi.append(wubi_dict["<UNK>"])

				Y.append(TAGS[0])

		length = len(X)
		if length != len(Y):
			return [], [], [], False
		if length > MAX_LEN:
			return [], [], [], False

		length = len(X_pinyin)
		if length != len(Y):
			return [], [], [], False
		if length > MAX_LEN:
			return [], [], [], False

		length = len(X_wubi)
		if length != len(Y):
			return [], [], [], False
		if length > MAX_LEN:
			return [], [], [], False

		for _ in xrange(length, MAX_LEN):
			X.append(0)
			X_pinyin.append(0)
			X_wubi.append(0)
			Y.append(0)

		strX = ' '.join(str(x) for x in X)
		strY = ' '.join(str(y) for y in Y)
		new_piece = strX + ' ' + strY + '\n'
		new_pieces.append(new_piece)

		strX_pinyin = ' '.join(str(x) for x in X_pinyin)
		strY = ' '.join(str(y) for y in Y)
		new_piece_pinyin = strX_pinyin + ' ' + strY + '\n'
		new_pieces_pinyin.append(new_piece_pinyin)

		strX_wubi = ' '.join(str(x) for x in X_wubi)
		strY = ' '.join(str(y) for y in Y)
		new_piece_wubi = strX_wubi + ' ' + strY + '\n'
		new_pieces_wubi.append(new_piece_wubi)

	return new_pieces, new_pieces_pinyin, new_pieces_wubi, True

# char pos labeling
def POS_Analyze(pieces, vob_dict, pos_dict, max_len = 100):
	global MAX_LEN
	MAX_LEN = max_len

	new_pieces = []
	for piece in pieces:
		ustr = piece.decode("utf-8").strip()
		lst = ustr.split()

		X = []
		Y = []

		for token in lst:
			index = token[::-1].find(u'/') + 1
			end = len(token) - index
			word = token[ : end]
			pos = token[end + 1 : ]

			pos_no = pos_dict["UNK"]
			if pos_dict.has_key(pos):
				pos_no = pos_dict[pos]

			leng = len(word)
			if leng > 1:
				for j, char in enumerate(word):
					if vob_dict.has_key(char):
						X.append(vob_dict[char])
					else:
						X.append(vob_dict[u"<UNK>"])

					if j == 0:
						Y.append(4 * pos_no + TAGS[1])
					elif j == leng - 1:
						Y.append(4 * pos_no + TAGS[3])
					else:
						Y.append(4 * pos_no + TAGS[2])
			else:
				if vob_dict.has_key(word):
					X.append(vob_dict[word])
				else:
					X.append(vob_dict[u"<UNK>"])

				Y.append(4 * pos_no + TAGS[0])

		length = len(X)
		if length != len(Y):
			return [], False
		if length > MAX_LEN:
			return [], False

		for _ in xrange(length, MAX_LEN):
			X.append(0)
			Y.append(0)

		strX = ' '.join(str(x) for x in X)
		strY = ' '.join(str(y) for y in Y)
		new_piece = strX + ' ' + strY + '\n'
		new_pieces.append(new_piece)

	return new_pieces, True


'''with open("pieces.txt", "w") as opt:
	cut_count = SliceSentence("gold_test.txt", opt)'''
