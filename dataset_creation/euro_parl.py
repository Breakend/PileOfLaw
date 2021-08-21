# Processes data from the European Parliament Proceedings Parallel Corpus 1996-2011 from 
# https://www.statmt.org/europarl/. We only use the English data. We strip out all tags. 

from bs4 import BeautifulSoup
import os
import glob
import random
from tqdm import tqdm 
import json

URL = "https://www.statmt.org/europarl/"
DATA_DIR = "../../data/europarl"
OUT_DIR = "../../data/europarl/processed"

def save_to_file(data, fpath):
    with open(fpath, "w") as out_file:
        for x in data:
            out_file.write(json.dumps(x) + "\n")
    print(f"Written {len(data)} to {fpath}")

def process_file(f):
    doc = []
    with open(f, "r") as in_file: 
        for line in in_file: 
            line = line.strip()
            if "<" in line or len(line) == 0:
                continue
            doc.append(line)
    return "\n".join(doc)
            

def main():
    
    # load data 
    in_glob = os.path.join(DATA_DIR, "txt", "en", "*.txt")
    files = glob.glob(in_glob)
    print(f"Found {len(files)} files.")

    # parse files
    docs = []
    for f in tqdm(files):
        text = process_file(f)
        doc = {
            "url": URL,
            "timestamp": "05-15-2012",
            "text": text
        }
        docs.append(doc)
    
    # shuffle and split into train / validation 
    random.seed(0)
    random.shuffle(docs)
    train = docs[:int(len(docs)*0.75)]
    validation = docs[int(len(docs)*0.75):]

    save_to_file(train, os.path.join(OUT_DIR, "train.euro_parl.jsonl"))
    save_to_file(validation, os.path.join(OUT_DIR, "validation.euro_parl.jsonl"))




if __name__ == "__main__":
    main()