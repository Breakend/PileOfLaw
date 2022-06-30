import os
import requests
import numpy as np
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import textract
import random
import datetime

try:
    import lzma as xz
except ImportError:
    import pylzma as xz

# Hacky, but this is just for scraping, just uncomment the one you want.
#url = "https://law.stanford.edu/office-of-student-affairs/bar-exam-information/"
url = "https://adamshajnfeld.weebly.com/"


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # This is chrome, you can set whatever browser you like
#If there is no such folder, the script will create one automatically
folder_location = './cache/'
if not os.path.exists(folder_location):
    os.mkdir(folder_location)

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
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser") 
docs = []
for link in soup.select("a[href$='.doc']"):
    #Name the pdf files using the last portion of each link which are unique in this case
    filename = os.path.join(folder_location,link['href'].split('/')[-1])
    if not os.path.exists(filename):
        with open(filename, 'wb') as f:
            f.write(requests.get(urljoin(url,link['href']), headers=headers).content)
    text = textract.process(filename)
    
    docs.append({
        "url" : link['href'],
        "text" : str(text),
        "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
        "created_timestamp" : "08-30-2006" if "stanford" in url else "02-01-2013" # though we don't have an exact date for when the docs were created, 
                                           # the author graduated in 2006 and I assume took the bar then and 
                                           # created these for the bar so I'm assuming 2006
                                           # if it's the adam website, he state that he took the bar in feb 2013
    })
for link in soup.select("a[href$='.docx']"):
    #Name the pdf files using the last portion of each link which are unique in this case
    filename = os.path.join(folder_location,link['href'].split('/')[-1])
    if not os.path.exists(filename):
        with open(filename, 'wb') as f:
            f.write(requests.get(urljoin(url,link['href']), headers=headers).content)
    text = textract.process(filename)
    docs.append({
        "url" : link['href'],
        "text" : str(text),
        "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
        "created_timestamp" : "08-30-2006" if "stanford" in url else "02-01-2013" # though we don't have an exact date for when the docs were created, 
                                           # the author graduated in 2006 and I assume took the bar then and 
                                           # created these for the bar so I'm assuming 2006
                                           # if it's the adam website, he state that he took the bar in feb 2013
    })

random.seed(0) # important for shuffling
rand_idx = list(range(len(docs)))
random.shuffle(rand_idx)

train_idx = rand_idx[:int(len(rand_idx)*0.75)]
val_idx = rand_idx[int(len(rand_idx)*0.75):]

train_docs = np.array(docs)[train_idx]
val_docs = np.array(docs)[val_idx]

if "stanford" in url:
    save_to_processed(train_docs, val_docs, "stanfordbarexamoutlines", "./cache/")
elif "adam" in url:
    save_to_processed(train_docs, val_docs, "shajnfeldbarexamoutlines", "./cache/")
