# -*- coding: utf-8 -*-
# Processes CFR XML files. 
# Raw XML can be downloaded from: https://www.govinfo.gov/bulkdata/CFR/2020/CFR-2020.zip

import xml.etree.ElementTree as ET
import glob
import os
import json
import random
from tqdm import tqdm
random.seed(0) # important for shuffling

# FILE PATHS
RAW_PATH = "../data/cfr/raw" # path to title folders
OUT_PATH = "../data/cfr/processed" # path to write data out to


files = glob.glob(os.path.join(RAW_PATH, "title-*/*.xml"))
print(f"{len(files)} total documents.")
outputs = []
for file in tqdm(files): 
    doc_name = file.split("/")[-1]
    tree = ET.parse(file)
    all_text = ET.tostring(tree.getroot(), encoding='utf-8', method='text')
    outputs.append({
        "text": all_text.decode("utf-8"),
        "url": "https://www.govinfo.gov/bulkdata/CFR/2020/CFR-2020.zip",
        "timestamp": "08-17-2021"
    })

random.shuffle(outputs)
train = outputs[:int(len(files)*0.75)]
val = outputs[int(len(files)*0.75):]

# save to processed 
tf = os.path.join(OUT_PATH, "train.cfr.jsonl")
with open(tf, "w") as out_file:
    for o in train: 
        out_file.write(json.dumps(o) + "\n")
print(f"Written {len(train)} documents to {tf}")

vf = os.path.join(OUT_PATH, "validation.cfr.jsonl")
with open(vf, "w") as out_file:
    for o in val: 
        out_file.write(json.dumps(o) + "\n")
print(f"Written {len(val)} documents to {vf}")