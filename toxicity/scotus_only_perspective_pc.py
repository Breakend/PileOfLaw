# Detects toxic language with unitariyai/detoxify
from collections import defaultdict
from tqdm.contrib.concurrent import process_map  # or thread_map


import csv
import glob
import os
import json
import numpy as np
import math
import random
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

API_KEY = "<Your Perspective API Key>"
# DATA DIRS
DATA_URL = 'pile-of-law/pile-of-law'


client = discovery.build(
    "commentanalyzer",
    "v1alpha1",
    developerKey=API_KEY,
    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
    static_discovery=False,
    )

SPLITS = ['train', 'validation']

# Threshold probabilities
PROFANITY_THRESHOLD_PROB = 0.8

MAX_LEN = int(1000000 / 10)

def exponential_backoff(req):
    for n in range(10):
        try:
            return client.comments().analyze(body=req).execute()
        except HttpError as error:
            if error.resp.reason.strip() not in ["Too Many Requests", "Resource has been exhausted (e.g. check quota)."]:
                print(error.resp.reason)
                raise
            if n < 9:
                time.sleep((random.random() * 5 * n) + random.random())
                print(f"BACKING OFF {n} for {error.resp.reason}") 
            else:
                raise
        else:
            break

def _conver_label_to_score(l):
    if l["label"] == "LABEL_0":
        return 1 - l["score"]
    else:
        return l["score"]

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def perspective_check_lexnlp(sentences):

    current_sentence_idx = 0
    results = defaultdict(dict)
    for sentence in sentences:
        # for idx, sentence in enumerate(sentences):
            # TODO: batching?

        analyze_request = {
            'comment': { 'text': sentence.strip()},
            'spanAnnotations' : False,
            "languages" : ["en"],
            'requestedAttributes':{"TOXICITY": {}, "SEVERE_TOXICITY": {}, "IDENTITY_ATTACK" : {}, "INSULT" : {}, "PROFANITY" : {}, "THREAT" : {}}
        }
        try:
            response = exponential_backoff(analyze_request)
        except Exception as e:
            results[current_sentence_idx]["ERROR"] = 1.0
            print(f"ERROR ON SENTENCE {sentence} {e}")

        for k, v in response["attributeScores"].items():
            results[current_sentence_idx][k] = v["summaryScore"]['value']
        current_sentence_idx += 1

    return results


def scrub_doc(doc):
    doc_text = doc["text"]
 
    sentences = lexnlp.get_sentence_list(doc_text)
    results_p = perspective_check_lexnlp(sentences)
    _return = {}
    if len(sentences) == 0:
        _return = {}
        _return["num_sentences"] =  len(sentences)
        _return["examples"] = json.dumps({})
        _return["confusion"] = json.dumps(np.zeros((4,4)), cls=NumpyEncoder)
    
    _return["sentences"] = json.dumps(sentences)        
    _return["perspective_scores"] = json.dumps(results_p)
    _return["num_sentences"] =  len(sentences)
    return _return


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
    from datasets import Dataset
    df = Dataset.from_dict({k: [dic[k] for dic in opinions] for k in opinions[0].keys()})
    results2 = df.map(scrub_doc, num_proc=32)
    del opinions

    with open(os.path.join(base_dir, "perspective_scores_pc_only.csv"), "w") as scores_f:
        spamwriter = csv.writer(scores_f)
        spamwriter.writerow(["DocIndex", "SentenceIndex", "API", "Category", "Score", "Date", "Name"])
        for results in [results2]:
            for i, (result, name, date) in enumerate(zip(results,names, dates)):  
                for t in ["perspective"]: 
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
