# -*- coding: utf-8 -*-

def MergeSentence(instream, cut_count, out_file, blacklist = []):
	# add one tail to prevent overflow of cut_count
	cut_count.append(-1)

	with open(out_file, 'w') as opt:
		i = 0
		cnt = cut_count[0]
		for line in instream:
			if i in blacklist:
				opt.write("Cannot handle this sentence!\n")
				i += 1
				cnt = cut_count[i]

				continue

			if cnt == 1:
				opt.write(line)
				i += 1
				cnt = cut_count[i]
			else:
				line = line.strip()
				opt.write(line + ' ')
				cnt -= 1
