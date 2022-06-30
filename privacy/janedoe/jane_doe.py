import torch
import pandas as pd
import mxnet as mx
import re
import names
import numpy as np
import json
from mlm.scorers import MLMScorer, MLMScorerPT, LMScorer
from mlm.models import get_pretrained

import numpy as np

sheet_id = "1zf2xfYJ0dvmSVFHUATvDXqG8TFX3Gmt1CppiWTyscg0"
sheet_name = "Sheet1"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

df = pd.read_csv(url, on_bad_lines='skip')

df["Text"].dropna()



ctxs = [mx.gpu(0)] # or, e.g., [mx.gpu(0), mx.gpu(1)]
model_name = 'pile-of-law/legalbert-large-1.7M-2'
model, vocab, tokenizer = get_pretrained(ctxs, model_name)
scorer = MLMScorerPT(model, vocab, tokenizer, ctxs)

insensitive_hippo = re.compile(re.escape('jane doe'), re.IGNORECASE)
insensitive_hippo2 = re.compile(re.escape(' doe '), re.IGNORECASE)
insensitive_hippo3 = re.compile(re.escape('jane roe'), re.IGNORECASE)
insensitive_hippo4 = re.compile(re.escape(' roe '), re.IGNORECASE)

average_diff = []

for sent in list(df["Text"].dropna()):
    replacement_sentences = [sent]
    for i in range(2):
        new_name = names.get_full_name(gender="female")
        new_sent = insensitive_hippo.sub(new_name, sent)
        new_sent = insensitive_hippo2.sub(" " + new_name + " ", new_sent)
        new_sent = insensitive_hippo3.sub(new_name, new_sent)
        new_sent = insensitive_hippo4.sub(" " + new_name + " ", new_sent)
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

    with open(f"jane_doe_diffs_{model_name.split('/')[-1]}.json", "w") as f:
        f.write(json.dumps(average_diff))

