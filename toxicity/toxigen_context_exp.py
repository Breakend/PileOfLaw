# Detects toxic language with unitariyai/detoxify
from collections import defaultdict
from tqdm.contrib.concurrent import process_map  # or thread_map
from multiprocess import set_start_method
set_start_method('spawn', force=True)
import pandas as pd

import csv
import glob
import os
import json
import numpy as np
import math
import random
import pickle
import argparse
from profanity_check import predict_prob
from detoxify import Detoxify
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
from joblib import load

from transformers import pipeline

base_dir = "./"

PIPE = None


def toxigen_roberta():
    # This will load the pipeline on demand on the current PROCESS/THREAD.
    # And load it only once.
    global PIPE
    if PIPE is None:
        PIPE = pipeline("text-classification", model="tomh/toxigen_roberta", device=0)
    return PIPE

import os

# DATA DIRS
DATA_URL = 'pile-of-law/pile-of-law'


SPLITS = ['train', 'validation']

# Threshold probabilities
PROFANITY_THRESHOLD_PROB = 0.8

MAX_LEN = int(1000000 / 10)



def _conver_label_to_score(l):
    if l["label"] == "LABEL_0":
        return 1 - l["score"]
    else:
        return l["score"]

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def toxigen(sentences):
    results = {}
    predictions = toxigen_roberta()(sentences)
    for i in range(len(sentences)):
        results[i] = { "TOXICITY" : _conver_label_to_score(predictions[i]) }
    return results


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

def main(args):
    toxigen_scores = pd.read_csv("./perspective_scores_toxigen_only.csv")
    toxigen_scores = toxigen_scores.nlargest(5000,['Score'])
    toxigen_scores = toxigen_scores[toxigen_scores["Score"] > .5]
    print(len(toxigen_scores))
    with open("./sent_mapping.pkl", "rb") as f:
        sentence_dict = pickle.load(f)
    from torch.utils.data import Dataset

    class MyDataset(Dataset):

        def __init__(self) -> None:
            super().__init__()
            self.data = []
            for i, row in sorted(toxigen_scores.iterrows(), key=lambda x: x[1]["Score"], reverse=True):
                sents = []
                low = max(0, row["SentenceIndex"]-2)
                doc_length = max(sentence_dict[row["DocIndex"]].keys())+1
                high = min(doc_length, row["SentenceIndex"]+2)
                for i in range(low, high):
                    sents.append(sentence_dict[row["DocIndex"]][i]["sent"])
                sentence = " ".join(sents)
                self.data.append(
                    {
                        "sentence_idx" : row["SentenceIndex"],
                        "doc_idx" : row["DocIndex"],
                        "prev_score" : row["Score"],
                        "text" : sentence,
                        "prev_sentence" : sentence_dict[row["DocIndex"]][row["SentenceIndex"]]["sent"]
                    })
        def __len__(self):
            return len(self.data)
            
        def __getitem__(self, i):
            return self.data[i]["text"]


    dataset = MyDataset()


    results1 = []
    sentences = []
    prev_sentences = []
    prev_scores = []
    cur_doc = defaultdict(dict)
    cur_doc_idx = 0
    for i, out in enumerate(tqdm(toxigen_roberta()(dataset, batch_size=32, truncation=True, max_length=512), total=len(dataset))):
        if cur_doc_idx != dataset.data[i]["doc_idx"]:
            cur_doc_idx = dataset.data[i]["doc_idx"]
            results1.append({"toxigen_scores" : json.dumps(cur_doc)})
            cur_doc = defaultdict(dict)
        cur_doc[dataset.data[i]["sentence_idx"]] = { "TOXICITY_DIFF" :  _conver_label_to_score(out) - dataset.data[i]["prev_score"]}
        sentences.append(dataset.data[i]["text"])
        prev_sentences.append(dataset.data[i]["prev_sentence"])
        prev_scores.append(dataset.data[i]["prev_score"])
    if len(cur_doc) > 0:
        results1.append({"toxigen_scores" : json.dumps(cur_doc)})
        cur_doc = defaultdict(dict)


    with open(os.path.join(base_dir, "perspective_scores_toxigen_only_context_exp.csv"), "w") as scores_f:
        spamwriter = csv.writer(scores_f)
        spamwriter.writerow(["DocIndex", "SentenceIndex", "API", "Category", "Score", "PrevScore", "PrevSentence", "CurSentence"])
        for results in [results1]:
            for i, (result, prev_score, prev_sentence, cur_sentence) in enumerate(zip(results, prev_scores, prev_sentences, sentences)):  
                for t in ["profanity_check", "perspective", "toxigen"]: 
                    if f"{t}_scores" not in result:
                        continue
                    scores = json.loads(result[f"{t}_scores"])
                    # doc number
                    for k, v in scores.items():
                        for k2, v2 in v.items():
                            datarow = (i, k, t, k2, v2, prev_score, prev_sentence, cur_sentence)
                            spamwriter.writerow(datarow)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--split")
    parser.add_argument("--name")

    args = parser.parse_args()
    main(args)
