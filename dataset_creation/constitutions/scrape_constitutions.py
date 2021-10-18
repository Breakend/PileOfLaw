

url= "https://www.constituteproject.org/service/constitutions?in_force=true"
url_template = "https://www.constituteproject.org/constitution/{const_id}?lang=en"

from bs4 import BeautifulSoup
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
ids = [r["id"] for r in response.json()]
overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.constitutions.xz", open_type)
val_f = xz.open("./cache/validation.constitutions.xz", open_type)

for _id in ids:
    print(_id)
    url = url_template.format(const_id= _id)
    response = requests.get(url, headers=headers)
    if not response.from_cache:
        time.sleep(random.random()*2)
    soup = BeautifulSoup(response.content)
    constitution_text_sections = soup.find_all("div", {"class" : "constitution-content__copy"})
    title = soup.find("h1", {"class" : "clearfix"}).get_text()
    text = title
    for section in constitution_text_sections:    
        text += section.get_text()
        text += "\n"

    datapoint = {
        "text" : text,
        "created_timestamp" : "",
        "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
        "url" : url
    }

    # This dataset is already heavily US biased, so it would be really weird not to train on the US
    # constitution
    if random.random() > .75 and "United_States" not in _id:
        val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
    else:
        train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))

