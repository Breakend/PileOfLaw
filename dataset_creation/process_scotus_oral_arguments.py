# Script for extracting transcript data from SCOTUS Oral Arguments. 
# Source: https://github.com/walkerdb/supreme_court_transcripts/releases/tag/2021-08-14
# We prepend the speaker to each line of text. Where the speaker is unknown, we use "Speaker"

import glob
import json
import os
import random
from tqdm import tqdm

URL = "https://github.com/walkerdb/supreme_court_transcripts/releases/tag/2021-08-14"
IN_DIR = "../../data/scotus_oral/supreme_court_transcripts-2021-08-14/oyez/cases/"
OUT_DIR = "../../data/scotus_oral/processed"

def process_transcript(d):
    doc = []
    try:
        for el in d["transcript"]['sections']:
            for turn in el['turns']:
                speaker = "Speaker"
                if turn['speaker'] is not None:
                    speaker = turn['speaker']['name']
                text = [t['text'] for t in turn['text_blocks']]
                text = " ".join(text)
                text = f"{speaker}: {text}"
                doc.append(text)
    except:
        print(d)
    return "\n".join(doc)

def save_to_file(data, fpath):
    with open(fpath, "w") as out_file:
        for x in data:
            out_file.write(json.dumps(x) + "\n")
    print(f"Written {len(data)} to {fpath}")

def main():
    
    in_files = glob.glob(os.path.join(IN_DIR, "*t*.json"))

    docs = [] 
    for f in tqdm(in_files):
        data = json.load(open(f))
        if data['unavailable'] or data['transcript'] is None:
            continue
        text = process_transcript(data)
        doc = {
            "url": URL,
            "timestamp": "08-12-2021",
            "text": text
        }
        docs.append(doc) 
    
    # shuffle and split into train / validation 
    random.seed(0)
    random.shuffle(docs)
    train = docs[:int(len(docs)*0.75)]
    validation = docs[int(len(docs)*0.75):]

    save_to_file(train, os.path.join(OUT_DIR, "train.scotus_oral.jsonl"))
    save_to_file(validation, os.path.join(OUT_DIR, "validation.scotus_oral.jsonl"))



    
    

if __name__ == "__main__":
    main()