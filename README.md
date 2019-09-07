# Multiple Embeddings for Chinese Word Segmentation

_Created by [Jingkang Wang*](http://www.cs.toronto.edu/~wangjk/), [Jianing Zhou*](https://zhjjn.github.io)，[Jie Zhou](https://github.com/SannyZhou) and [Gongshen Liu](https://github.com/wangjksjtu/multi-embedding-cws)._

## Introduction
In this paper, we introduce multiple character embeddings including ___Pinyin Romanization___ and ___Wubi Input___, both of which are easily accessible and effective in depicting semantics of characters. To fully leverage them, we propose a novel shared Bi-LSTM-CRF model, which fuses multiple features efficiently. Extensive experiments on five corpora demonstrate that extra embeddings help obtain a significant improvement. Specifically, we achieves the state-of-the-art performance in __AS and CITYU corpora with F1 scores 96.9 and 97.3__, respectively.

In this repository, we release code and data for reproducing the results given in the [paper](https://www.aclweb.org/anthology/P19-2029) (ACL-SRW 2019).

## Requirements
- Python 2.7 or 3.5+
- Tensorflow 1.2+
- CUDA 8.0+ (For GPU)
- Python Libraries: numpy, cPickle, __pypinyin__

## Citation
If you find our work is helpful and relevant, please consider citing

```
@inproceedings{multi-embed2019,
  author    = {Jianing Zhou and
               Jingkang Wang and
	       Jie Zhou and
               Gongshen Liu},
  title     = {Multiple Character Embeddings for Chinese Word Segmentation},
  booktitle = {{ACL} {(2)}},
  pages     = {210--216},
  publisher = {Association for Computational Linguistics},
  year      = {2019}
}
```

## Reproduce Results
### 1. Data Preparation
#### Preprocessing

```
python preprocess.py --rootDir Corpora --corpusAll Corpora/all.txt --resultFile pre_chars_for_w2v.txt
python getpinyin.py
python getwubi.py
```
    
If you want to use your own data, please replace `Corpora` to the path of your corpus. Run `python preprocess.py -h` to see more details.

#### Word2vec Training
```
./third_party/word2vec -train pre_chars_for_w2v.txt -save-vocab pre_vocab.txt -min-count 3
./third_party/word2vec -train pre_pinyin_for_w2v.txt -save-vocab pre_vocab_pinyin.txt -min-count 3
./third_party/word2vec -train pre_wubi_for_w2v.txt -save-vocab pre_vocab_wubi.txt -min-count 3
```

```
python SentHandler/replace_unk.py pre_vocab.txt pre_chars_for_w2v.txt chars_for_w2v.txt
python SentHandler/replace_unk.py pre_vocab_pinyin.txt pre_pinyin_for_w2v.txt pinyin_for_w2v.txt
python SentHandler/replace_unk.py pre_vocab_wubi.txt pre_wubi_for_w2v.txt wubi_for_w2v.txt
```
```
./third_party/word2vec -train chars_for_w2v.txt -output char_vec.txt -size 256 -sample 1e-4 -negative 0 -hs 1 -binary 0 -iter 5
./third_party/word2vec -train pinyin_for_w2v.txt -output pinyin_vec.txt -size 256 -sample 1e-4 -negative 0 -hs 1 -binary 0 -iter 5
./third_party/word2vec -train wubi_for_w2v.txt -output wubi_vec.txt -size 256 -sample 1e-4 -negative 0 -hs 1 -binary 0 -iter 5
```
```
./third_party/word2vec -train chars_for_w2v.txt -output char_vec300.txt -size 300 -sample 1e-4 -negative 0 -hs 1 -binary 0 -iter 5
./third_party/word2vec -train pinyin_for_w2v.txt -output pinyin_vec300.txt -size 300 -sample 1e-4 -negative 0 -hs 1 -binary 0 -iter 5
./third_party/word2vec -train wubi_for_w2v.txt -output wubi_vec300.txt -size 300 -sample 1e-4 -negative 0 -hs 1 -binary 0 -iter 5
```
First, the file **word2vec.c** in `third_party` directory should be compiled (see `third_party/compile_w2v.sh`). Also, you could directly add executive permission to the `third_party/word2vec` using `chmod +x third_party/word2vec`. Second, the word2vec tool counts the characters which have a frequency more than 3 and saves them into file **pre_vocab.txt**. After that, the scripts replace the words that are not in `pre_vocab.txt` with **"UNK"**. Finally, word2vec training process begins.

#### Data Partition
```
python pre_train.py --corpusAll Corpora/msr/train-all.txt --char_vecpath char_vec.txt --pinyin_vecpath pinyin_vec.txt --wubi_vecpath wubi_vec.txt --train_file Corpora/msr/ --test_file Corpora/msr/ --test_file_raw Corpora/msr/test_raw.txt --test_file_gold Corpora/msr/test_gold.txt
python pre_train.py --corpusAll Corpora/msr300/train-all.txt --char_vecpath char_vec300.txt --pinyin_vecpath pinyin_vec300.txt --wubi_vecpath wubi_vec300.txt --train_file Corpora/msr300/ --test_file Corpora/msr300/ --test_file_raw Corpora/msr300/test_raw.txt --test_file_gold Corpora/msr300/test_gold.txt
```

To see HELP for the training script:
```
python pre_train.py -h
```

### 2. Model Training
```
python ./CWSTrain/fc_lstm3_crf_train.py --train_data_path Corpora/msr --test_data_path Corpora/msr --word2vec_path char_vec.txt --pinyin2vec_path pinyin_vec.txt --wubi2vec_path wubi_vec.txt --log_dir Logs_fc_lstm3/msr --embedding_size 256 --batch_size 256

python ./CWSTrain/pw_lstm3_crf_train.py --train_data_path Corpora/msr --test_data_path Corpora/msr --word2vec_path char_vec.txt --pinyin2vec_path pinyin_vec.txt --wubi2vec_path wubi_vec.txt --log_dir Logs_pw_lstm3/msr --embedding_size 256 --batch_size 256

python ./CWSTrain/share_lstm3_crf_train.py --train_data_path Corpora/msr --test_data_path Corpora/msr --word2vec_path char_vec.txt --pinyin2vec_path pinyin_vec.txt --wubi2vec_path wubi_vec.txt --log_dir Logs_share_lstm3/msr --embedding_size 256 --batch_size 256

python ./CWSTrain/nopy_fc_lstm3_crf_train.py --train_data_path Corpora/msr --test_data_path Corpora/msr --word2vec_path char_vec.txt --wubi2vec_path wubi_vec.txt --log_dir Logs_nopy/msr --embedding_size 256 --batch_size 256*

python ./CWSTrain/nowubi_fc_lstm3_crf_train.py --train_data_path Corpora/msr --test_data_path Corpora/msr --word2vec_path char_vec.txt --pinyin2vec_path pinyin_vec.txt --log_dir Logs_nowubi/msr --embedding_size 256 --batch_size 256
```
If you want to train on other corpora, please change the train_data_path, test_data_path and make a new log directory. Arguments of __\*\_lstm\*\_crf\_train.py__ are set by **tf.app.flags**.

### 3. Word Segmentation
#### Freeze graph
```
python tools/freeze_graph.py --input_graph Logs_fc_lstm3/msr/graph.pbtxt --input_checkpoint Logs_fc_lstm3/msr/model.ckpt --output_node_names "input_placeholder_char,input_placeholder_pinyin,input_placeholder_wubi,transitions,Reshape_11" --output_graph Models/fc_lstm3_crf_model_msr.pbtxt

python tools/freeze_graph.py --input_graph Logs_nopy/msr/graph.pbtxt --input_checkpoint Logs_nopy/msr/model.ckpt --output_node_names "input_placeholder_char,input_placeholder_wubi,transitions,Reshape_11" --output_graph Models/nopy_fc_lstm3_crf_model_msr.pbtxt

python tools/freeze_graph.py --input_graph Logs_nowubi/msr/graph.pbtxt --input_checkpoint Logs_nowubi/msr/model.ckpt --output_node_names "input_placeholder_char,input_placeholder_pinyin,transitions,Reshape_11" --output_graph Models/nowubi_fc_lstm3_crf_model_msr.pbtxt
```
Build model for segmentation.

#### Dump Vocabulary

```
python tools/vob_dump.py --char_vecpath char_vec.txt --pinyin_vecpath pinyin_vec.txt --wubi_vecpath wubi_vec.txt --char_dump_path Models/char_dump.pk --pinyin_dump_path Models/pinyin_dump.pk --wubi_dump_path Models/wubi_dump.pk

python tools/vob_dump.py --char_vecpath char_vec300.txt --pinyin_vecpath pinyin_vec300.txt --wubi_vecpath wubi_vec300.txt --char_dump_path Models/char_dump300.pk --pinyin_dump_path Models/pinyin_dump300.pk --wubi_dump_path Models/wubi_dump300.pk
```
Note that this step is **neccessary** for the seg model.

#### Seg Script
Use file **tools/crf_seg.py** to segment words utilizing pre-trained models. You could refer to this file for detailed parameter configurations.
```
python tools/crf_seg.py --test_data Corpora/msr/test_raw.txt --model_path Models/fc_lstm3_crf_model_msr.pbtxt --result_path Results/crf_result_msr.txt

python tools/fc_lstm3_crf_seg_nopy.py --test_data Corpora/msr/test_raw.txt --model_path Models/nopy_fc_lstm3_crf_model_msr.pbtxt --result_path Results/nopy_crf_result_msr.txt

python tools/fc_lstm3_crf_seg_nowubi.py --test_data Corpora/msr/test_raw.txt --model_path Models/nowubi_fc_lstm3_crf_model_msr.pbtxt --result_path Results/nowubi_crf_result_msr.txt
```
#### PRF Scoring
```
python PRF_Score.py Results/crf_result_msr.txt Corpora/msr/test_gold.txt
```
Result files are put in directory **Results/**.

## Acknowledgements
This code is based on the this repo ([LSTM-CNN-CWS](https://github.com/MeteorYee/LSTM-CNN-CWS)). Many thanks to the author.

## License
Our code is released under MIT License.
