url = "https://archive.org/download/us-inspectors-general.bulk/us-inspectors-general.bulk.zip"

import zipfile
import os
import datetime
import random
try:
    import lzma as xz
except ImportError:
    import pylzma as xz

cache_path = "./cache/us-inspectors-general.bulk.zip"
if not os.path.exists(cache_path):
    import wget
    filename = wget.download(url, out="./cache/")

import os
import zipfile
overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.oig.xz", open_type)
val_f = xz.open("./cache/validation.oig.xz", open_type)
import os, json

i = 0
with zipfile.ZipFile(cache_path) as z:
    for filename in z.namelist():
        if not os.path.isdir(filename) and ".txt" in filename:
            # read the file
            with z.open(filename) as f:
                year = filename.split("/")[1]
                text = str(f.read())

                datapoint = {
                    "url" : url,
                    "text" : text,
                    "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
                    "created_timestamp" : year
                }

                if random.random() > .75:
                    val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
                else:
                    train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
                i += 1

                if i % 5000 == 0: print(i)