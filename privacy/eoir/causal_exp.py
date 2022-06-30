import json
from datasets import load_dataset
import spacy
from citeurl import Citator
citator = Citator()

from collections import Counter
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def build_vocab(texts, max_vocab=10000, min_freq=3):
    nlp = spacy.load("en_core_web_sm") # just the tokenizer
    wc = Counter()
    for doc in nlp.pipe(texts):
        citations = citator.list_cites(doc.text)
        for x in citations:
            wc[str(x).lower()] += 1
        for word in doc:
            if word.ent_type_ == "CARDINAL":
                continue
            if is_number(word.text):
                continue
            if len(word.text.strip()) <= 2:
                continue
            wc[word.lower_] += 1

    word2id = {}
    id2word = {}
    for word, count in wc.most_common():
        if count < min_freq: break
        if len(word2id) >= max_vocab: break
        wid = len(word2id)
        word2id[word] = wid
        id2word[wid] = word
    return list([x for x in word2id.keys()]) 

process = True 
if process:
    dataset = load_dataset("pile-of-law/eoir_privacy", "all", split="all", use_auth_token=True)

    data = {}

    dataset.to_csv("descriptions.csv")

    import pandas as pd
    x = pd.read_csv("descriptions.csv")
    pseudo_label = { 0 : "no_pseudo",  1 : "pseudo"}
    x["label"] = [pseudo_label[z] for z in x["label"]]
    x = x.drop_duplicates("text")
    pres = pd.read_csv("presidents.csv")
    
    year_to_pres_map = {}
    for name, years in zip(pres["President Name"], pres["Years In Office"]):
        splitted_years = years.split("-")
        if splitted_years[-1].strip() == "":
            splitted_years = [splitted_years[0]]
        if len(splitted_years) > 1:
            for i in range(int(splitted_years[0]), int(splitted_years[1])+1):
                year_to_pres_map[i] = name
        else:
            year_to_pres_map[int(splitted_years[0])] = name

    x["president"] = [year_to_pres_map[int(year)] if is_number(year) and int(year) in year_to_pres_map.keys() else "UNK" for year in x["year"]]
    x = x[[pres != "UNK" for pres in x["president"]]]
    x = x[[True if is_number(year) else False for year in x["year"]]]

    x.to_csv("descriptions.csv")

    vocab = build_vocab(dataset["text"])
    with open("vocab.txt", "w") as f:
        for v in vocab:
            f.write(v + "\n")

with open("vocab.txt", "r") as f:
    vocab = [x.strip() for x in f.readlines()]

print("Finished vocab!")
import causal_attribution
merged_scores = {}
for method in ["residualization"]:
    for hidden_size in [512]:
        for lr in [7e-4]:
            importance_scores = causal_attribution.score_vocab(
                vocab=vocab,
                scoring_model=method,
                hidden_size = hidden_size,
                lr=lr,
                train_steps = 3000,
                max_seq_len=750,
                status_bar=True,
                use_gpu=True,
                csv="descriptions.csv",
                delimiter=",",
                name_to_type={
                        'text': 'input',
                        #'name' : 'control',
                        #'president' : 'control',
                        'year' : 'control',
                        'label': 'predict'
                })
            for (key, value) in importance_scores["label"]["pseudo"]:
                if key not in merged_scores:
                    merged_scores[key] = []
                merged_scores[key].append(value)

averaged = {}
import numpy as np
for key, val in merged_scores.items():
    averaged[key] = np.mean(val)

with open("averaged_results.json", "w") as f:
    f.write(json.dumps(averaged))
import pdb; pdb.set_trace()
