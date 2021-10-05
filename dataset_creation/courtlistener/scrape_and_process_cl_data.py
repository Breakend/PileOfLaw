import wget
import json
import os
import tarfile
from tqdm import tqdm
from pathlib import Path
import io
import json
import tempfile
import datetime
import bs4
import random
import shutil


try:
    import lzma as xz
except ImportError:
    import pylzma as xz
url = "https://www.courtlistener.com/api/bulk-data/opinions/all.tar"

if not os.path.exists("./cache/all.tar"):
    import wget
    filename = wget.download(url, out="./cache/")



def idempotent(x):
    return x


def html2text(x):
    soup = bs4.BeautifulSoup(x, "lxml")
    return soup.get_text()

field_order = [
    ("plain_text", idempotent),
    ("html", html2text),
    ("html_lawbox", html2text),
    ("html_columbia", html2text),
    ("html_with_citations", html2text),
    ("xml_harvard", html2text)
]

error_str = (
    "Unable to extract the content from this file. Please try reading the original."
)



def parse_json(item):
    """ From https://github.com/thoppe/The-Pile-FreeLaw/blob/master/P1_extract_text.py
    """

    js = json.loads(item)

    text = None

    if "html" in js and js["html"] == error_str:
        return None

    for k, func in field_order:
        if k in js and isinstance(js[k], str) and len(js[k]):
            text = func(js[k])

    if text is None:
        print(f"Skipping {item}, couldn't find text.")
        return None

    return {
            "url" : js['resource_uri'],
            "text" : text,
            "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
            "created_timestamp" : datetime.datetime.strptime(js['date_created'].split("T")[0], '%Y-%m-%d').strftime("%m-%d-%Y")
        }

train = 0
val = 0

with xz.open("./cache/train.courtlisteneropinions.xz", 'w') as train_f:
    with xz.open("./cache/validation.courtlisteneropinions.xz", 'w') as val_f:
        with tarfile.open("./cache/all.tar") as all_tar:
            for jxd in all_tar.getmembers():
                with tarfile.open(fileobj=all_tar.extractfile(jxd)) as jxd_tar:
                    for opinion in jxd_tar.getmembers():
                        datapoint = parse_json(jxd_tar.extractfile(opinion).read())
                        if random.random() > .75:
                            val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
                            val += 1
                        else:
                            train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
                            train += 1
                        
                        total, used, free = shutil.disk_usage("/")

                        if train % 10000 == 0:
                            print(f"Have {train} documents and {val} validation documents!")
                            print("Total: %d GiB" % (total // (2**30)))
                            print("Used: %d GiB" % (used // (2**30)))
                            print("Free: %d GiB" % (free // (2**30)))

                        if (free // (2**30)) < 30:
                            print("RUNNING OUT OF DISK!!!")
                        if (free // (2**30)) < 25:
                            print("Too little disk!!!")
                            break

print(f"Have {train} documents and {val} validation documents!")


                        