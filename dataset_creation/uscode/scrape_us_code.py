url = "https://uscode.house.gov/download/releasepoints/us/pl/117/49/xml_uscAll@117-49.zip"

import zipfile
import os
import textract
import random
import bs4
import json
import datetime
try:
    import lzma as xz
except ImportError:
    import pylzma as xz

cache_path = "./cache/xml_uscAll@117-49.zip"
if not os.path.exists(cache_path):
    import wget
    filename = wget.download(url, out="./cache/")

with zipfile.ZipFile(cache_path, 'r') as zip_ref:
    zip_ref.extractall("./cache/")

overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.uscode.xz", open_type)
val_f = xz.open("./cache/validation.uscode.xz", open_type)
def html2text(x):
    soup = bs4.BeautifulSoup(x, "lxml")
    return soup.get_text()

docs = []
for path, subdirs, files in os.walk("./cache/"):
    for name in files:
        if not name.endswith(".xml"):
            continue
        with open(os.path.join(path, name), "r") as text_file:
            text = html2text(text_file.read())
        # text = str(textract.process(os.path.join(path, name)))
        datapoint = {
            "text" : text,
            "created_timestamp" : "2021",
            "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
            "url" : url
        }

        if random.random() > .75:
            val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
        else:
            train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))