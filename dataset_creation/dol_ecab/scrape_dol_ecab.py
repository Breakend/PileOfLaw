from bs4 import BeautifulSoup
import requests_cache
import os
import time
import os
import textract
import numpy as np
import json
import random
import datetime
import re
import pandas as pd

try:
    import lzma as xz
except ImportError:
    import pylzma as xz

cache = "./cache"

requests = requests_cache.CachedSession('scotus')
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

if not os.path.exists(cache):
    os.mkdir(cache)

docs = []
base_url = "https://www.dol.gov/agencies/ecab/decisions/{year}/{month}"
pdf_url = "https://www.dol.gov/sites/dolgov/files/ecab/decisions/{year}/{month}/{tag}.pdf"

docs_for_pseudonyms = []

num_pseudonyms = 0

for vol in range(2007,2023):
    for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
        url = base_url.format(year=vol, month=month)
        # page2 = requests.get(url, headers=headers)
        # soup = BeautifulSoup(page2.text,"lxml")
        converters = {c: lambda x: str(x) for c in range(3)}
        try:
            table = pd.read_html(url, converters=converters)
        except:
            print(f"Skipping {month} {vol} b/c table formatting issue.")

        for row in table[0].iterrows():
            tag, date, casename = row[1].values

            link = pdf_url.format(year=vol, month=month, tag=tag)

            print(tag)
            if not os.path.exists(f'{cache}/{tag}.pdf'):
                print(link)
                pdf = requests.get(link, headers=headers)

                with open(f'{cache}/{tag}.pdf', 'wb') as f:
                    f.write(pdf.content)

            try:
                text = textract.process(f'{cache}/{tag}.pdf', encoding='utf-8')
                text = text.decode("utf8")
            except:
                print(f"Skipping {tag}!")
                continue

            try:
                datetime_object = datetime.datetime.strptime(date, '%B %d, %Y')
            except:
                try:
                    datetime_object = datetime.datetime.strptime(date, '%B%d, %Y')
                except:
                    date = " ".join(date.split(" ")[:-1])
                    try:
                        datetime_object = datetime.datetime.strptime(date, '%B %d, %Y')
                    except:
                        continue
            timestamp = datetime_object.strftime("%m-%d-%Y")

            if len(text) < 100:
                import pdb; pdb.set_trace()

            docs.append({
                "text" : text,
                "created_timestamp" : timestamp,
                "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
                "url" : link
            })


def save_to_processed(train, val, source_name, out_path):
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    tf = os.path.join(out_path, f"train.{source_name}.jsonl")
    with open(tf, mode='w', encoding='utf-8') as out_file:
        for line in train:
            out_file.write(json.dumps(line) + "\n")
    print(f"Written {len(train)} documents to {tf}")

    vf = os.path.join(out_path, f"validation.{source_name}.jsonl")
    with open(vf, mode='w', encoding='utf-8') as out_file:
        for line in val:
            out_file.write(json.dumps(line) + "\n")
    print(f"Written {len(val)} documents to {vf}")

    # now compress with lib
    print("compressing files...")
    with open(vf, 'rb') as f, open(vf+".xz", 'wb') as out:
        out.write(xz.compress(bytes(f.read())))
    with open(tf, 'rb') as f, open(tf+".xz", 'wb') as out:
        out.write(xz.compress(bytes(f.read())))
    print("compressed")

random.seed(0) # important for shuffling
rand_idx = list(range(len(docs)))
random.shuffle(rand_idx)

train_idx = rand_idx[:int(len(rand_idx)*0.75)]
val_idx = rand_idx[int(len(rand_idx)*0.75):]

train_docs = np.array(docs)[train_idx]
val_docs = np.array(docs)[val_idx]

save_to_processed(train_docs, val_docs, "dol_ecab", "./cache/")
