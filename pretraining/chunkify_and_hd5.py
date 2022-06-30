import os, sys
import argparse
import time
import tqdm
from collections import namedtuple
from multiprocessing import Pool
import re
import traceback
import lzma
import json
from pathlib import Path
import numpy as np
import nltk
import random
import lexnlp.nlp.en.segments.sentences
from tqdm import tqdm
from nltk.tokenize import RegexpTokenizer
from transformers import BertTokenizerFast
import h5py
import transformers
transformers.logging.set_verbosity_error()

MaskedLmToken = namedtuple("MaskedLmToken", ["idx", "token"])
with open('vocab.txt') as f:
    VOCAB = [x.strip() for x in f.readlines()]

tokenizer = BertTokenizerFast(
    "vocab.txt",
    clean_text=True,
    handle_chinese_chars=True,
    strip_accents=True,
    lowercase=True,
    max_len=128
)

def token_mask_sentence_pair(tokens, masked_lm_prob=0.15, max_predictions_per_seq=20, vocab=VOCAB, random_generator=random):
    """Mask a sentence pair for the masked LM objective"""
    cand_idx = []
    tokens = [vocab[i] for i in tokens]
    for idx, token in enumerate(tokens):
        # We don't mask special tokens, [CLS] and [SEP]
        if token == "[CLS]" or token == "[SEP]" or token == "[PAD]":
            continue
        cand_idx.append(idx)

    random_generator.shuffle(cand_idx)
    output_tokens = list(tokens)
    num_masks = min(max_predictions_per_seq, max(1, int(round(len(tokens) * masked_lm_prob))))

    masked_lms = []
    covered_idx = set()

    for idx in cand_idx:
        if len(masked_lms) >= num_masks:
            break
        if idx in covered_idx:
            continue
        covered_idx.add(idx)

        # 80% of the time the token is masked with [MASK]
        # 10% of the time the token is masked with the original token
        # 10% of the time the token is masked with random token in the vocab
        mask_token = None

        if random_generator.random() < 0.8:
            mask_token = "[MASK]"
        else:
            if random_generator.random() < 0.5:
                mask_token = tokens[idx]
            else:
                mask_token = random.choice(vocab[5:]) 

        output_tokens[idx] = mask_token

        # MaskedLmToken = collections.namedtuple("MaskedLmToken", ["idx", "token"])
        masked_lms.append(MaskedLmToken(idx=idx, token=tokens[idx]))

    masked_lms = sorted(masked_lms, key=lambda x: x.idx)

    masked_lm_positions = []
    masked_lm_tokens = []
    for masked_lm in masked_lms:
        masked_lm_positions.append(masked_lm.idx)
        masked_lm_tokens.append(masked_lm.token)
        
    masked_lm_positions = masked_lm_positions + [0] * (max_predictions_per_seq -
                                                                     len(masked_lm_positions))
    masked_lm_tokens = masked_lm_tokens + ["[PAD]"] * (max_predictions_per_seq - len(masked_lm_tokens))


    return (output_tokens, masked_lm_positions, masked_lm_tokens)

def write_sentence_pairs_to_hdf5(sentence_pairs, output_file):
    """Write sentence pairs into hdf5 file"""

    f = h5py.File(output_file, 'w')
    f.create_dataset("input_ids", data=np.array([x["input_ids"] for x in sentence_pairs]), dtype='i4', compression='gzip')
    f.create_dataset("input_mask",
                     data=np.array([x["attention_mask"] for x in sentence_pairs]),
                     dtype='i1',
                     compression='gzip')
    f.create_dataset("segment_ids",
                     data=np.array([x["token_type_ids"] for x in sentence_pairs]),
                     dtype='i1',
                     compression='gzip')
    f.create_dataset("masked_lm_positions",
                     data=np.array([x["masked_lm_positions"] for x in sentence_pairs]),
                     dtype='i4',
                     compression='gzip')
    f.create_dataset("masked_lm_ids",
                     data=np.array([x["masked_lm_ids"] for x in sentence_pairs]),
                     dtype='i4',
                     compression='gzip')
    f.create_dataset("next_sentence_labels",
                     data=np.array([x["next_sentence_label"] for x in sentence_pairs]),
                     dtype='i1',
                     compression='gzip')

    f.flush()
    f.close()




tp = "train"
strPath = "./unzipped/"
fileList = os.listdir(strPath)
fileList = [os.path.join(strPath, item) for item in fileList if item.endswith(".jsonl") and item.startswith(f"{tp}.")]
i = 0
total_size = np.sum([os.path.getsize(x) for x in fileList])

chunks = 256
maxsize = total_size / chunks
print(f"MAX_SIZE {maxsize}")

_tp_map = { 
        "train" : "training",
        "validation" : "test"
        }

def segment_art(article, num_words=56):

    # First we segment into a bundle sentences that would be roughly num_words long.
    # and with some probability we include some shorter versions.
    # We add a [SEP] token in between intermediate sentences to get around upstream problems.

    segments = []
    article = re.sub("\s+"," ", article)
    article = re.sub("-+","-", article)
    article = re.sub("_+","_", article)
    _stime = time.time()
    sentences = lexnlp.nlp.en.segments.sentences.get_sentence_list(article)
    cur_segment = ""
    cur_segment_wordcount = 0
    i = 0
    # TODO: if really want to capture all content need a sliding window (for j in range(len(sentences); i= j
    for i, cur_sentence in enumerate(sentences):
        if cur_segment_wordcount + len(cur_sentence) >= 200 and len(cur_segment) > 0:
            segments.append(cur_segment)
            cur_segment = ""
            cur_segment_wordcount = 0
        cur_segment += cur_sentence
        cur_segment_wordcount += len(cur_sentence)

    if cur_segment != "":
        segments.append(cur_segment)

    if len(segments) == 1:
        segments = [segments[0][:int(len(segments)/2)], segments[0][int(len(segments)/2):]]

    sentences_a = []
    sentences_b = []
    for segment_a, segment_b in pairwise(segments):
        if segment_a is None or segment_b is None:
            continue
        sentences_a.append(segment_a)
        sentences_b.append(segment_b)
    assert len(sentences_a) == len(sentences_b)

    if len(sentences_a) == 0:
        print(segments)
        print(article)
        return [], []
    _etime = time.time()
    total_segment_info = []

    _stime = time.time()
    stuff = tokenizer(sentences_a, sentences_b, padding='max_length', truncation=True)
    _etime = time.time()
    #print(f"Time to tokenize sentences: {_etime - _stime}")
    _stime = time.time()
    
    rez = [token_mask_sentence_pair(x) for x in stuff["input_ids"]]
    output_tokens_p, masked_lm_positions_p, masked_lm_tokens_p = zip(*rez)
    _etime = time.time()
    #print(f"Time to mask sentences: {_etime - _stime}")


    for input_ids, token_type_ids, attention_mask, output_tokens, masked_lm_positions, masked_lm_tokens in zip(stuff["input_ids"], stuff["token_type_ids"], stuff["attention_mask"], output_tokens_p, masked_lm_positions_p, masked_lm_tokens_p):
        total_segment_info.append({
            "input_ids" : tokenizer.convert_tokens_to_ids(output_tokens),
            "token_type_ids" : token_type_ids,
            "attention_mask" : attention_mask,
            "masked_lm_positions" : masked_lm_positions,
            "masked_lm_tokens" : tokenizer.convert_tokens_to_ids(masked_lm_tokens),
            "next_sentence_label" : 0
            })
    return total_segment_info

output_dir = "./chunkified_and_processed/"
current_chunk = 0
current_file = None
random.shuffle(fileList)
all_segments = []
import itertools
def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return list(zip(a, b))

parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('fileno', help='Description for bar argument', type=int)
args = parser.parse_args()
_segments_cache = []
z = 0
_cached_lines = []
all_segments = []
_file_handles = [open(f'intermediate_chunkfication/{args.fileno}_{i}.jsonl', 'w') for i in range(chunks)]
with open(fileList[args.fileno], 'r') as _jsonfile:
    print(f"{fileList[args.fileno]}...")
    for line in _jsonfile.readlines(): 
        if line is None:
            continue
        _loaded = json.loads(line)
        if _loaded is not None:
            _loaded = _loaded['text'] 
        else:
            continue
        segmented_raw_data = segment_art(_loaded)
        for segments in segmented_raw_data:
            random.choice(_file_handles).write(f"{json.dumps(segments)}\n")
     
for _file in _file_handles:
    _file.close()
