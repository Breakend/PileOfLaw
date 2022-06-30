
from bs4 import BeautifulSoup
import requests_cache
import os
import time
import os
from tqdm import tqdm
import numpy as np
import json
import random
import re
import pickle
import datetime
try:
    import lzma as xz
except ImportError:
    import pylzma as xz

overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./train.canadian_decisions.xz", open_type)
val_f = xz.open("./validation.canadian_decisions.xz", open_type)

with open("canada_cases.pickle", "rb") as f:
    _pickled = pickle.load(f)

for key, value in _pickled.items():
    if "The specific page has either moved or is no longer part" in value['text']:
        continue


    datapoint = {
        "text" : value['text'],
        "created_timestamp" : value['year'],
        "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
        "url" : "https://www.bccourts.ca/search_judgments.aspx?obd={}&court=1#SearchTitle" if value["jdx"] == "bc" else "https://www.ontariocourts.ca/coa/decisions_main"
    }

    if random.random() > .75:
        val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
    else:
        train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))

train_f.close()
val_f.close()
