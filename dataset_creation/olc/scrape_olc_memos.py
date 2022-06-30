from bs4 import BeautifulSoup
import requests
import os
import time
import os
import textract
import numpy as np
import json
import random
import datetime

try:
    import lzma as xz
except ImportError:
    import pylzma as xz

cache = "./cache"

if not os.path.exists(cache):
    os.mkdir(cache)
base_url = "https://www.justice.gov/olc/opinions"

pages = 138
docs = []

def _get_opinions(soup):
    g_data = soup.findAll("td", {"class": "views-field-field-opinion-attachment-file"})
    g_dates = soup.findAll("span", {"class" : "date-display-single"})
    for data, date in zip(g_data, g_dates):
        link = "https://www.justice.gov/" + data.find("a")["href"]
        tag = link.split("/")[-2]
        if not os.path.exists(f'{cache}/{tag}.pdf'):
            print(link)
            pdf = requests.get(link)

            with open(f'{cache}/{tag}.pdf', 'wb') as f:
                f.write(pdf.content)

        text = str(textract.process(f'{cache}/{tag}.pdf'))

        issuance_date = date.text
        print(issuance_date) 
        issuance_date = issuance_date.replace("/", "-")
        docs.append({
            "text" : text,
            "created_timestamp" : issuance_date,
            "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
            "url" : link
        })


pages = 138
page2 = requests.get(base_url)

soup = BeautifulSoup(page2.text, "lxml")
button_next = soup.find("a", {"title": "Go to next page"}, href=True)

_get_opinions(soup)

while button_next:
    time.sleep(2)#delay time requests are sent so we don\'t get kicked by server
    url2 = "https://www.justice.gov{0}".format(button_next["href"])
    page2=requests.get(url2)
    soup=BeautifulSoup(page2.text,"lxml")
    _get_opinions(soup)
    button_next = soup.find("a", {"title": "Go to next page"}, href=True)

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

save_to_processed(train_docs, val_docs, "olcmemos", "./cache/")

