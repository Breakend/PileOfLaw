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
overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.cc_casebooks.xz", open_type)
val_f = xz.open("./cache/validation.cc_casebooks.xz", open_type)
# ASSUMES THAT YOUVE DOWNLOADED THE TEXTBOOKS INTO THE CACHE AND THAT THEY'RE ALL CC LICENSE
docs = []
for path, subdirs, files in os.walk("./cache/"):
    for name in files:
        if not name.endswith(".pdf"):
            continue
        text = str(textract.process(os.path.join(path, name)))
        datapoint = {
            "text" : text,
            "created_timestamp" : "",
            "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
            "url" : "https://open.umn.edu/opentextbooks/"
        }

        if random.random() > .75:
            val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
        else:
            train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))