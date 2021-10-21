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
url_template = "https://www.ftc.gov/policy/advisory-opinions?page={page}"


overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.ftc_advisory_opinions.xz", open_type)
val_f = xz.open("./cache/validation.ftc_advisory_opinions.xz", open_type)

for page in range(0, 20):
    print(page)

    url = url_template.format(page = page)
    response = requests.get(url, headers=headers)
    soup= BeautifulSoup(response.text, "html.parser")     
    potential_links = soup.select("a[href$='.pdf']")
    # import pdb; pdb.set_trace()
    potential_links = [link for link in potential_links if "advisory_opinions" in link["href"]]
    # potential_dates = [d.get_text() for d in soup.find_all("span", {"class" : "date-display-single"})]

    # assert len(potential_dates) == len(potential_links) 
    if len(potential_links) == 0:
        print(f"SKipping for year {page} because no pdf links")
        continue
    
    for link in potential_links:
        try:
            response = requests.get(link["href"], headers=headers)
        except:
            print(f"PROBLEM GETTING {link}")
            time.sleep(random.random()*5)
            continue

        if not response.from_cache:
            time.sleep(random.random()*2.)

        
        with open(f'{cache}/{link["href"].split("/")[-1]}', 'wb') as f:
            f.write(response.content)

        try:
            text = str(textract.process(f'{cache}/{link["href"].split("/")[-1]}'))
        except:
            print(f"Problem with {link['href']}")
            continue
        if len(text) < len('\\x0c\\x0c') * 2:
            try:
                text = str(textract.process(f'{cache}/{link["href"].split("/")[-1]}', method='tesseract'))
            except:
                print(f"Problem with {link['href']}")
                continue
        if len(text) < len('\\x0c\\x0c') * 2:
            continue 

        os.remove(f'{cache}/{link["href"].split("/")[-1]}')
        datapoint = {
            "text" : text,
            "created_timestamp" : "",
            "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
            "url" : link["href"]
        }
        # import pdb; pdb.set_trace()
        if random.random() > .75:
            val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
        else:
            train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))