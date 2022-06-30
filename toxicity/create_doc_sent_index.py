# Detects toxic language with unitariyai/detoxify
from collections import defaultdict
from tqdm.contrib.concurrent import process_map  # or thread_map
from multiprocess import set_start_method
set_start_method('spawn', force=True)


from collections import defaultdict
import csv
import glob
import os
import json
import numpy as np
import math
import random
import argparse
from detoxify import Detoxify
from tqdm import tqdm
from datasets import load_dataset
from multiprocessing import Pool, cpu_count
import lexnlp.nlp.en.segments.sentences as lexnlp
from googleapiclient import discovery
import time

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
        "name" : stuff["name"],
        "docket_number" : stuff["docket_number"],
        "citations" : [x["cite"] for x in stuff["citations"]]
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

    from torch.utils.data import Dataset

    class MyDataset(Dataset):

        def __init__(self) -> None:
            super().__init__()
            self.data = defaultdict(dict)
            for doc_idx, opinion in enumerate(opinions):
                sentences = lexnlp.get_sentence_list(opinion["text"])
                for sentence_idx, sentence in enumerate(sentences):
                    self.data[doc_idx][sentence_idx] = {
                            "sent" : sentence,
                            "name" : opinion["name"],
                            "docket_number" : opinion["docket_number"],
                            "decision_date" : opinion["decision_date"],
                            "citations" : opinion["citations"]
                            }

        def __len__(self):
            return len(self.data)
            
        def __getitem__(self, i):
            return self.data[i]["text"]


    dataset = MyDataset()
    import pickle
    with open("sent_mapping.pkl", "wb") as f:
        pickle.dump(dataset.data, f)






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--split")
    parser.add_argument("--name")

    args = parser.parse_args()
    main(args)
