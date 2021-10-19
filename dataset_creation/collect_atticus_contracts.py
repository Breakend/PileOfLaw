# Code for formatting unlabelled Atticus contract data from: https://github.com/TheAtticusProject/cuad

import glob
import os
import random
from tqdm import tqdm
import datetime 
import json 

IN_DIR = "../../data/atticus_contract/contracts/"
OUT_DIR = "../../data/atticus_contract/processed"


def save_to_file(data, fpath):
    with open(fpath, "w") as out_file:
        for x in data:
            out_file.write(json.dumps(x) + "\n")
    print(f"Written {len(data)} to {fpath}")

def main():

    # load contracts 
    files = glob.glob(os.path.join(IN_DIR, "*", "*.txt"))
    print(f"Collected {len(files)} contracts")
    docs = []
    for f in files: 
        text = ""
        with open(f) as in_file: 
            for line in in_file:
                text = text + line
        
        doc = {
            "url": "https://github.com/TheAtticusProject/cuad",
            "created_timestamp": "",
            "timestamp": datetime.date.today().strftime("%m-%d-%Y"),
            "text": text
        }
        docs.append(doc) 
    
    # shuffle and split into train / validation 
    random.seed(0)
    random.shuffle(docs)
    train = docs[:int(len(docs)*0.75)]
    validation = docs[int(len(docs)*0.75):]

    save_to_file(train, os.path.join(OUT_DIR, "train.atticus_contracts.jsonl"))
    save_to_file(validation, os.path.join(OUT_DIR, "validation.atticus_contracts.jsonl"))



if __name__ == "__main__":
    main()