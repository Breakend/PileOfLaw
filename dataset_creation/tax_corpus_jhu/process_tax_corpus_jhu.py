import os
import random
import json
import datetime
import numpy as np
# Assumes you've downloaded 
link = "https://archive.data.jhu.edu/file.xhtml?persistentId=doi:10.7281/T1/N1X6I4/D5CQ0Y&version=2.0"
# into cache/ and extracted it
try:
    import lzma as xz
except ImportError:
    import pylzma as xz

with open('cache/plrs_tc_corpus_feb25.txt', 'r') as f:
    docs = [{
        "text" : " ".join(doc.split(" ")[1:]),
        "created_timestamp" : "",
        "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
        "url" : link
    } for doc in f.readlines()] # first word is always a file name

# Note the preprocessing in this dataset is very messy. In the future we may wish to find the raw original proceedings.

def save_to_processed(train, val, source_name, out_path):
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    tf = os.path.join(out_path, f"train.{source_name}.jsonl")
    with open(tf, mode='w', encoding='utf-8') as out_file:
        for line in train:
            out_file.write(json.dumps(line) + "\n")
    print(f"Written {len(train)} documents to {tf}")

    vf = os.path.join(out_path, f"validation.{source_name}.jsonl")
    with open(vf, mode='w', encoding='utf-8') as out_file:
        for line in val:
            out_file.write(json.dumps(line) + "\n")
    print(f"Written {len(val)} documents to {vf}")

    # now compress with lib
    print("compressing files...")
    with open(vf, 'rb') as f, open(vf+".xz", 'wb') as out:
        out.write(xz.compress(bytes(f.read())))
    with open(tf, 'rb') as f, open(tf+".xz", 'wb') as out:
        out.write(xz.compress(bytes(f.read())))
    print("compressed")

random.seed(0) # important for shuffling
rand_idx = list(range(len(docs)))
random.shuffle(rand_idx)

train_idx = rand_idx[:int(len(rand_idx)*0.75)]
val_idx = rand_idx[int(len(rand_idx)*0.75):]

train_docs = np.array(docs)[train_idx]
val_docs = np.array(docs)[val_idx]

save_to_processed(train_docs, val_docs, "taxrulings", "./cache/")
