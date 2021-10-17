import os
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
# TODO: can't actually get have to downlaod manually
url = "https://dataverse.harvard.edu/file.xhtml?fileId=4590189&version=6.0#"

cache_path = "./cache/UNGDC_1970-2020.tar.gz"
if not os.path.exists(cache_path):
    raise ValueError(f"Need to download from {url}")
    # import wget
    # filename = wget.download(url, out="./cache/")
import tarfile
overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.undebates.xz", open_type)
val_f = xz.open("./cache/validation.undebates.xz", open_type)
# if fname.endswith("tar.gz"):
tar = tarfile.open(cache_path, "r:gz")
tar.extractall()
tar.close()
for path, subdirs, files in os.walk("./TXT/"):
    for name in files:
        if not name.endswith(".txt") or name[0] == ".":
            continue
        
        with open(os.path.join(path, name), "r") as f:
            text = str(f.read())

        datapoint = {
            "text" : text,
            "created_timestamp" : name.split("_")[-1].replace(".txt", ""),
            "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
            "url" : url
        }

        if random.random() > .75:
            val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
        else:
            train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
