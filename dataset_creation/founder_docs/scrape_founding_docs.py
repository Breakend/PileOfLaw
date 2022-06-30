

url= "https://founders.archives.gov/Metadata/founders-online-metadata.json"
url_template = "https://www.constituteproject.org/constitution/{const_id}?lang=en"

from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
import requests_cache
import os
import time
import os
from tqdm import tqdm
import numpy as np
import json
import random
import datetime
requests = requests_cache.CachedSession('scotus')
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
try:
    import lzma as xz
except ImportError:
    import pylzma as xz

cache = "./cache"

if not os.path.exists(cache):
    os.mkdir(cache)


response = requests.get(url, headers=headers)
ids = [r["permalink"] for r in response.json()]
overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.founding_docs.xz", open_type)
val_f = xz.open("./cache/validation.founding_docs.xz", open_type)

for url in tqdm(ids):
    # url = url_template.format(const_id= _id)
    tag = url.split("documents/")[-1]
    url = f"https://founders.archives.gov/API/docdata/{tag}"
    response = requests.get(url, headers=headers)
    if not response.from_cache:
        time.sleep(.1)

    try:
        _dict = response.json()
    except:
        print("Problem loading response")
        print(response.content)
        continue
    text = f"Title: {_dict['title']}\nFrom: {','.join(_dict['authors'])}\nTo: {','.join(_dict['recipients'])}\n\n{_dict['content']}"
    if _dict['date-from'] is not None:
        created_date = "-".join(_dict['date-from'].split("-")[1:]) + "-" + _dict['date-from'].split("-")[0]
    else:
        created_date = ""

    datapoint = {
        "text" : text,
        "created_timestamp" : created_date,
        "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
        "url" : url
    }

    # This dataset is already heavily US biased, so it would be really weird not to train on the US
    # constitution
    if random.random() > .75:
        val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
    else:
        train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))

