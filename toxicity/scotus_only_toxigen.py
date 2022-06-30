# Detects toxic language with unitariyai/toxigen
from collections import defaultdict
from tqdm.contrib.concurrent import process_map  # or thread_map
from multiprocess import set_start_method
set_start_method('spawn', force=True)


import csv
import glob
import os
import json
import numpy as np
import math
import random
import argparse
from profanity_check import predict_prob
from tqdm import tqdm
from datasets import load_dataset
from multiprocessing import Pool, cpu_count
import lexnlp.nlp.en.segments.sentences as lexnlp
from googleapiclient import discovery
import time
from apiclient.errors import HttpError

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import RidgeClassifier
from sys import getsizeof

from transformers import pipeline

base_dir = "./"


PIPE = None

DATA_URL = 'pile-of-law/pile-of-law'


SPLITS = ['train', 'validation']

# Threshold probabilities
PROFANITY_THRESHOLD_PROB = 0.8

MAX_LEN = int(1000000 / 10)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def save_json_file(data, out_dir, filename):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
	filepath = os.path.join(out_dir, filename)
	with open(filepath, 'w') as out_file:
		json.dump(data, out_file)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def get_opinions(stuff):
    stuff = json.loads(stuff) 
    return {
        "text" : "\n".join(x["text"] for x in stuff["casebody"]["data"]["opinions"]),
        "decision_date" : stuff["decision_date"],
        "name" : stuff["name"]
    }

def toxigen_roberta():
    # This will load the pipeline on demand on the current PROCESS/THREAD.
    # And load it only once.
    global PIPE
    if PIPE is None:
        PIPE = pipeline("text-classification", model="tomh/toxigen_roberta", device=0, return_all_scores=True)
    return PIPE

import os

def main(args):
    set_start_method('spawn', force=True)
    split = args.split
    name = args.name
    print(f"{split}.{name}")
    results = []
    with open("data.jsonl", "r") as f:
        opinions = f.readlines()
        opinions = [get_opinions(x) for x in opinions]
        opinions = [x for x in opinions if len(x["text"]) > 3000]
        dates = [x["decision_date"] for x in opinions]
        names = [x["name"] for x in opinions]

    print(len(opinions))
    from torch.utils.data import Dataset

    class MyDataset(Dataset):

        def __init__(self) -> None:
            super().__init__()
            self.data = []
            for doc_idx, opinion in enumerate(opinions):
                sentences = lexnlp.get_sentence_list(opinion["text"])
                for sentence_idx, sentence in enumerate(sentences):
                    self.data.append(
                        {
                            "sentence_idx" : sentence_idx,
                            "doc_idx" : doc_idx,
                            "text" : sentence
                        })
        def __len__(self):
            return len(self.data)
            
        def __getitem__(self, i):
            return self.data[i]["text"]


    dataset = MyDataset()


    results1 = []
    cur_doc = defaultdict(dict)
    cur_doc_idx = 0
    try:
        for i, out in enumerate(tqdm(toxigen_roberta()(dataset, batch_size=32, truncation=True, max_length=512), total=len(dataset))):
            if cur_doc_idx != dataset.data[i]["doc_idx"]:
                cur_doc_idx = dataset.data[i]["doc_idx"]
                results1.append({"toxigen_scores" : json.dumps(cur_doc)})
                cur_doc = defaultdict(dict)
            cur_doc[dataset.data[i]["sentence_idx"]] = { x["label"] : x["score"] for x in out }

        if len(cur_doc) > 0:
            results1.append({"toxigen_scores" : json.dumps(cur_doc)})
            cur_doc = defaultdict(dict)
    except:
        import pdb; pdb.set_trace()


    with open(os.path.join(base_dir, "toxigen_scores.csv"), "w") as scores_f:
        spamwriter = csv.writer(scores_f)
        spamwriter.writerow(["DocIndex", "SentenceIndex", "API", "Category", "Score", "Date", "Name"])
        for results in [results1]:
            for i, (result, name, date) in enumerate(zip(results,names, dates)):  
                for t in ["toxigen"]: 
                    if f"{t}_scores" not in result:
                        continue
                    scores = json.loads(result[f"{t}_scores"])
                    # doc number
                    for k, v in scores.items():
                        for k2, v2 in v.items():
                            datarow = (i, k, t, k2, v2, date, name)
                            spamwriter.writerow(datarow)
                

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--split")
    parser.add_argument("--name")

    args = parser.parse_args()
    main(args)
