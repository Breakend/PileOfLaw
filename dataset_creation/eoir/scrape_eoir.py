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
base_url_27 = "https://www.justice.gov/eoir/volume-{vol:02}"
base_url_26 = "https://www.justice.gov/eoir/precedent-decisions-volume-{vol:02}"

docs_for_pseudonyms = []

num_pseudonyms = 0

for vol in range(8,29):
    if vol >= 27:
        url = base_url_27.format(vol=vol)
    else:
        url = base_url_26.format(vol=vol)
    page2 = requests.get(url, headers=headers)
    soup = BeautifulSoup(page2.text,"lxml")
    g_dates = soup.findAll("td", attrs={'class': None, "colspan" : None})
    g_data = soup.findAll("td", {"class" : "rteright"})

    for data, date in zip(g_data, g_dates):
        # data = data.find("a")
        if "justice.gov" in data.find("a")["href"]:
            link = data.find("a")["href"]
        else:
            link = "https://www.justice.gov/" + data.find("a")["href"]
        if link.endswith(".pdf"):
            tag = link.split("/")[-1].replace(".pdf", "")
        else:
            tag = link.split("/")[-2]
        tag += "__" + str(vol)
        print(tag)
        if not os.path.exists(f'{cache}/{tag}.pdf'):
            print(link)
            pdf = requests.get(link)

            with open(f'{cache}/{tag}.pdf', 'wb') as f:
                f.write(pdf.content)

        text = textract.process(f'{cache}/{tag}.pdf', encoding='utf-8')
        text = text.decode("utf8")
        
        try:
            name = date.find("strong").text.replace(",", "")
        except:
            try:
                name = date.find("b").text.replace(",", "")
            except:
                import pdb; pdb.set_trace()

        print(name)

        def check_pseudo(ns):
            ns = ns.replace("et al.", "").strip()
            ns = ns.replace("‑", "-")
            if ns == "DEF-" or ns == "D'O-" or ns == "DEN-" or ns == "DEG" or ns == "DE M-" or ns == "D-S- INC." or ns == "DIP-":
                return True
            for n in re.split('(&|and|AND)',ns):
                n = n.strip()
                n = n.replace(" ", "")
                created_pseudo = "-".join(n.replace("-", ""))
                if created_pseudo == n or created_pseudo + "-" == n:
                    return True
                created_pseudo = ".".join(n.replace(".", ""))
                if created_pseudo == n:
                    return True
            return False
                 
        is_pseudonym = check_pseudo(name)
        print(is_pseudonym)
        # if not is_pseudonym:
        #     import pdb; pdb.set_trace()

        if is_pseudonym:
            num_pseudonyms +=1 

        issuance_date = date.text.split("(")[-1].split(" ")[-1]
        issuance_date = issuance_date.replace(")", "").strip()
        print(issuance_date) 
        if issuance_date == "":
            import pdb; pdb.set_trace()

        if len(text) < 100:
            import pdb; pdb.set_trace()

        docs.append({
            "text" : text,
            "created_timestamp" : issuance_date,
            "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
            "url" : link
        })

        docs_for_pseudonyms.append({
            "text" : text,
            "created_timestamp" : issuance_date,
            "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
            "url" : link,
            "name" : name,
            "is_pseudonym" : is_pseudonym
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

save_to_processed(train_docs, val_docs, "eoir", "./cache/")

save_to_processed(docs_for_pseudonyms, [], "eoir_pseudonym", "./cache/")

print("NUM PSEUDOI")
print(num_pseudonyms)
