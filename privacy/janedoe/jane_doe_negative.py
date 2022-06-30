# -*- coding: utf-8 -*-
import json
import torch
import pandas as pd
from mlm.scorers import MLMScorer, MLMScorerPT, LMScorer
from mlm.models import get_pretrained
import pickle
import numpy as np

# To generate pickle, look to https://github.com/microsoft/biosbias
with open("BIOS.pkl", "rb") as f:
    sentences = pickle.load(f)[:500] 
    
import mxnet as mx
import re
import names
import numpy as np

ctxs = [mx.gpu(0)] # or, e.g., [mx.gpu(0), mx.gpu(1)]
model_name = 'pile-of-law/legalbert-large-1.7M-2' # Swap model name to use different model
model, vocab, tokenizer = get_pretrained(ctxs, model_name)
scorer = MLMScorerPT(model, vocab, tokenizer, ctxs)

import re


import names
average_diff = []

import random
for sent in list(sentences):
    sent = sent["bio"]

    replacement_sentences = [sent.replace("_", "Jane Doe")]

    for i in range(2):
        new_name = names.get_full_name(gender="female")
        new_sent = sent.replace("_", new_name) 
        replacement_sentences.append(new_sent)

    torch.cuda.empty_cache()
    with torch.no_grad():
        scores = scorer.score_sentences(replacement_sentences, split_size=51)
        main_score = scores[0]
        for i, x in enumerate(scores):
            if i == 0: continue
            diff = main_score - x
            average_diff.append(diff)
        print(np.mean(average_diff))

    with open(f"jane_doe_diffs_{model_name.split('/')[-1]}_negative.json", "w") as f:
        f.write(json.dumps(average_diff))

