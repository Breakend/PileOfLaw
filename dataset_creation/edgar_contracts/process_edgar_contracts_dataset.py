import os
import datetime
import random
import numpy as np
import json


try:
    import lzma as xz
except ImportError:
    import pylzma as xz
url = "https://applica-public.s3-eu-west-1.amazonaws.com/contract-discovery/edgar.txt.xz"

if not os.path.exists("./cache/edgar.txt.xz"):
    import wget
    filename = wget.download(url, out="./cache/")

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

docs = []

with xz.open('./cache/edgar.txt.xz', mode='rt') as f:
    for line in f:
        docs.append({
            "url" : url,
            "text" : line,
            "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
            "created_timestamp" : "" # Unfortunately the dataset that originally scraped the material didn't keep the date.
        })

random.seed(0) # important for shuffling
rand_idx = list(range(len(docs)))
random.shuffle(rand_idx)

train_idx = rand_idx[:int(len(rand_idx)*0.75)]
val_idx = rand_idx[int(len(rand_idx)*0.75):]

train_docs = np.array(docs)[train_idx]
val_docs = np.array(docs)[val_idx]

save_to_processed(train_docs, val_docs, "edgar", "./cache/")
