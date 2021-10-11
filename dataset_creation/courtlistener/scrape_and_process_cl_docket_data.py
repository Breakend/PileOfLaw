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
# url = "https://www.courtlistener.com/api/bulk-data/opinions/all.tar"

# if not os.path.exists("./cache/all.tar"):
#     import wget
#     filename = wget.download(url, out="./cache/")



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

import requests
import time
import random
import datetime
import json
import os

def requestJSON(url):
    while True:
        try:
            r = requests.get(url, headers={'Authorization': f'Token {os.environ["API_KEY"]}' })
            if r.status_code != 200:
                print('error code', r.status_code)
                time.sleep(5)
                continue
            else:
                break
        except Exception as e:
            print(e)
            time.sleep(5)
            continue
    return r.json()


next_page = "https://www.courtlistener.com/api/rest/v3/recap-documents/?is_available=true"

val=0
train=0
from dateutil.relativedelta import *
import datetime
import datefinder

if os.path.exists("./cache/cur_url.txt"):
    with open("./cache/cur_url.txt", "r") as f:
        next_page = f.read().strip()
        dates = list(datefinder.find_dates(next_page))
        cur_month = dates[0]
        prev_month = dates[1]
        if cur_month < prev_month:
            tmp = prev_month
            prev_month = cur_month
            cur_month = tmp
else:
    cur_month = datetime.datetime.now()
    prev_month = cur_month - relativedelta(days=3)
    next_page = f"https://www.courtlistener.com/api/rest/v3/docket-entries/?date_filed__lt={cur_month.strftime('%Y-%m-%d')}&date_filed__gt={prev_month.strftime('%Y-%m-%d')}&fields=date_filed%2Crecap_documents%2Cdescription&recap_documents__is_available=true"


with xz.open("./cache/train.courtlistenerdocketentries.xz", 'a') as train_f:
    with xz.open("./cache/validation.courtlistenerdocketentries.xz", 'a') as val_f:
        while True:
            #print(cur_month.strftime('%Y-%m-%d'))
            #next_page = f"https://www.courtlistener.com/api/rest/v3/docket-entries/?date_filed__lt={cur_month.strftime('%Y-%m-%d')}&date_filed__gt={prev_month.strftime('%Y-%m-%d')}&fields=date_filed%2Crecap_documents%2Cdescription&recap_documents__is_available=true"
            while next_page is not None:
                print(next_page)
                js_data = requestJSON(next_page)
                if 'count' in js_data:
                    print(js_data['count'])
                time.sleep(random.random()*3)
                next_page = js_data["next"]
                if next_page is not None:
                    with open('./cache/cur_url.txt', 'w') as f:
                        f.write(next_page)
                for docket_entry in js_data["results"]:
                    for recap_data in docket_entry["recap_documents"]:
                        if "plain_text" in recap_data and recap_data["plain_text"]:
                            datapoint = {
                                    "url" : recap_data['resource_uri'],
                                    "text" : recap_data["plain_text"],
                                    "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
                                    "created_timestamp" : docket_entry['date_filed']
                                }
                            if random.random() > .75:
                                val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
                                val += 1
                            else:
                                train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
                                train += 1
                        if train % 5000 == 0:
                            print(f"Have {train} documents and {val} validation documents!")
            
            cur_month = prev_month
            prev_month = cur_month - relativedelta(days=3)


                            
