import zipfile
import os
import datetime
import textract
import random
import json
try:
    import lzma as xz
except ImportError:
    import pylzma as xz
url = "https://files.consumerfinance.gov/a/assets/Credit_Card_Agreements_2021_Q2.zip"

cache_path = "./cache/Credit_Card_Agreements_2021_Q2.zip"
if not os.path.exists(cache_path):
    import wget
    filename = wget.download(url, out="./cache/")

with zipfile.ZipFile(cache_path, 'r') as zip_ref:
    zip_ref.extractall("./cache/")

overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.cfpb_cc.xz", open_type)
val_f = xz.open("./cache/validation.cfpb_cc.xz", open_type)

docs = []
for path, subdirs, files in os.walk("./cache/"):
    for name in files:
        if not name.endswith(".pdf"):
            continue
        text = str(textract.process(os.path.join(path, name)))
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