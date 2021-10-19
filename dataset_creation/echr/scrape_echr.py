import zipfile
import os
import datetime
try:
    import lzma as xz
except ImportError:
    import pylzma as xz
url = "https://archive.org/download/ECHR-ACL2019/ECHR_Dataset.zip"

cache_path = "./cache/ECHR_Dataset.zip"
if not os.path.exists(cache_path):
    import wget
    filename = wget.download(url, out="./cache/")

with zipfile.ZipFile(cache_path, 'r') as zip_ref:
    zip_ref.extractall("./cache/")


overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.echr.xz", open_type)
val_f = xz.open("./cache/validation.echr.xz", open_type)
import os, json

path_to_json = './cache/EN_train'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

for json_file in json_files:
    with open('./cache/EN_train/' + json_file, "r") as f:
        loaded = json.loads(f.read())

    blocklist = ["ITEMID"]
    text = ""
    for key, val in loaded.items():
        if val != "" and val is not None:
            if not isinstance(val, list):
                text += f"{key}: {val}\n"
            else:
                if len(val) > 0:
                    joined = '\n'.join(val)
                    text += f"{key}: {joined}\n"
    datapoint = {
        "url" : url,
        "text" : text,
        "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
        "created_timestamp" : loaded["DATE"]
    }

    train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))


path_to_json = 'cache/EN_dev'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

for json_file in json_files:
    with open( 'cache/EN_dev/'+ json_file, "r") as f:
        loaded = json.loads(f.read())

    blocklist = ["ITEMID"]
    text = ""
    for key, val in loaded.items():
        if val != "" and val is not None:
            if not isinstance(val, list):
                text += f"{key}: {val}\n"
            else:
                if len(val) > 0:
                    joined=  '\n'.join(val)
                    text += f"{key}: {joined}\n"
    datapoint = {
        "url" : url,
        "text" : text,
        "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
        "created_timestamp" : loaded["DATE"]
    }

    val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))

