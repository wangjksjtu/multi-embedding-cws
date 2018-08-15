# -*- coding: utf-8 -*-

import tensorflow as tf
import numpy as np
import cPickle as cpk
import argparse


def load_graph(frozen_graph_filename):
    # We load the protobuf file from the disk and parse it to retrieve the
    # unserialized graph_def
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    # Then, we can use again a convenient built-in function to import a graph_def into the
    # current default Graph
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(
            graph_def,
            input_map=None,
            return_elements=None,
            name="prefix",
            op_dict=None,
            producer_op_list=None
        )

    return graph

# make the raw data acceptable for the model
def TransRawData(test_data, vob_char_dict, vob_pinyin_dict, vob_wubi_dict, MAX_LEN):
    inp = open(test_data, 'r')
    X_char = []
    X_pinyin = []
    X_wubi = []

    for line in inp:
        ustr = line.decode("utf-8").strip()
        lX_char = []
        lX_pinyin = []
        lX_wubi = []
        for char in ustr:
            if vob_char_dict.has_key(char):
                lX_char.append(vob_char_dict[char])
            else:
                lX_char.append(vob_char_dict[u"<UNK>"])
            if vob_pinyin_dict.has_key(char):
                lX_pinyin.append(vob_pinyin_dict[char])
            else:
                lX_pinyin.append(vob_pinyin_dict[u"<UNK>"])
            if vob_wubi_dict.has_key(char):
                lX_wubi.append(vob_wubi_dict[char])
            else:
                lX_wubi.append(vob_wubi_dict[u"<UNK>"])

        for _ in xrange(len(ustr), MAX_LEN):
            lX_char.append(0)
            lX_pinyin.append(0)
            lX_wubi.append(0)

        X_char.append(lX_char)
        X_pinyin.append(lX_pinyin)
        X_wubi.append(lX_wubi)

    inp.close()
    return np.array(X_char), np.array(X_pinyin), np.array(X_wubi)

def seg_sequence(graph, tX_char, tX_pinyin, tX_wubi, batch_size):
    inp_char_op = graph.get_operation_by_name("prefix/input_placeholder_char")
    inp_char = inp_char_op.outputs[0]

    inp_pinyin_op = graph.get_operation_by_name("prefix/input_placeholder_pinyin")
    inp_pinyin = inp_pinyin_op.outputs[0]

    inp_wubi_op = graph.get_operation_by_name("prefix/input_placeholder_wubi")
    inp_wubi = inp_wubi_op.outputs[0]

    trans_node = graph.get_operation_by_name("prefix/transitions")
    transitions = trans_node.outputs[0]

    label_node = graph.get_operation_by_name("prefix/Reshape_11")
    label_scores = label_node.outputs[0]

    results = []
    with tf.Session(graph = graph) as sess:
        totalLen = tX_char.shape[0]
        numBatch = int((totalLen - 1) / batch_size) + 1

        for i in xrange(numBatch):
            endOff = (i + 1) * batch_size
            if endOff > totalLen:
                endOff = totalLen

            feed_dict = {inp_char : tX_char[i * batch_size : endOff], inp_pinyin : tX_pinyin[i * batch_size : endOff], inp_wubi : tX_wubi[i * batch_size : endOff]}
            unary_scores, transMatrix = sess.run(
              [label_scores, transitions], feed_dict)

            for unary_score in unary_scores:
                viterbi_sequence, _ = tf.contrib.crf.viterbi_decode(
                  unary_score, transMatrix)

                results.append(viterbi_sequence)

    return results

def main(model_path, test_data, char_path, pinyin_path, wubi_path, result_path, MAX_LEN, batch_size):
    # load model
    graph = load_graph(model_path)

    # load vocabulary
    try:
        dip_char = open(char_path, 'r')
        vob_char_dict = cpk.load(dip_char)
        dip_char.close()
        dip_pinyin = open(pinyin_path, 'r')
        vob_pinyin_dict = cpk.load(dip_pinyin)
        dip_pinyin.close()
        dip_wubi = open(wubi_path, 'r')
        vob_wubi_dict = cpk.load(dip_wubi)
        dip_wubi.close()
    except Exception as e:
        raise e

    # get test data
    tX_char, tX_pinyin, tX_wubi = TransRawData(test_data, vob_char_dict, vob_pinyin_dict, vob_wubi_dict, MAX_LEN)

    # get predicted sequence
    sequences = seg_sequence(graph, tX_char, tX_pinyin, tX_wubi, batch_size)

    rinp = open(test_data, 'r')
    with open(result_path, 'w') as opt:
        for ind, line in enumerate(rinp):
            ustr = line.strip().decode("utf-8")
            seq = sequences[ind]
            newline = u""
            for word, label in zip(ustr, seq):
                if label == 0 or label == 1:
                    newline += u' ' + word
                else:
                    newline += word

            newline = newline.strip().encode("utf-8")
            opt.write(newline + '\n')

    rinp.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
      "--model_path",
      type = str,
      default = "Models/fc_lstm3_crf_model.pbtxt",
      help = "model path")
    parser.add_argument(
      "--test_data",
      type = str,
      default = "Corpora/test_raw.txt",
      help = "data to be tested")
    parser.add_argument(
      "--char_path",
      type = str,
      default = "Models/char_dump.pk",
      help = "vocabulary")
    parser.add_argument(
      "--pinyin_path",
      type = str,
      default = "Models/pinyin_dump.pk",
      help = "vocabulary")
    parser.add_argument(
      "--wubi_path",
      type = str,
      default = "Models/wubi_dump.pk",
      help = "vocabulary")
    parser.add_argument(
      "--result_path",
      type = str,
      default = "Results/crf_result.txt",
      help = "result file will be output here")

    parser.add_argument(
      "--MAX_LEN",
      type = int,
      default = 80,
      help = "max sentencen length")
    parser.add_argument(
      "--batch_size",
      type = int,
      default = 100,
      help = "batch size")

    args = parser.parse_args()
    main(args.model_path, args.test_data, args.char_path, args.pinyin_path,
        args.wubi_path, args.result_path, args.MAX_LEN, args.batch_size)
