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
url_template = "https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/{year}-{n}.html"


overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.scotus_docket_entries.xz", open_type)
val_f = xz.open("./cache/validation.scotus_docket_entries.xz", open_type)

for year in list(range(18, 22))[::-1]:

    print(year)
    if year == 21:
        vals = range(1,558)
    elif year == 20:
        vals = range(1, 8478)
    elif year == 19:
        vals = range(1, 8930)
    elif year == 18:
        vals = range(1, 9849)
    else:
        raise ValueError("blerg")

    for n in vals:
        url = url_template.format(year=year, n=n)
        response = requests.get(url, headers=headers)
        soup= BeautifulSoup(response.text, "html.parser")     
        potential_links = soup.select("a[href$='.pdf']")
        # import pdb; pdb.set_trace()
        potential_links = [link for link in potential_links if "DocketPDF" in link["href"]]
        
        if len(potential_links) == 0:
            print(f"SKipping for year {year} at n {n} because no pdf links")
            continue
        
        for link in potential_links:
            try:
                response = requests.get(link["href"], headers=headers)
            except:
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

            os.remove(f'{cache}/{link["href"].split("/")[-1]}')
            datapoint = {
                "text" : text,
                "created_timestamp" : f'{link["href"].split("/")[-1][4:6]}-{link["href"].split("/")[-1][6:8]}-{link["href"].split("/")[-1][0:4]}',
                "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
                "url" : link["href"]
            }
            if random.random() > .75:
                val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
            else:
                train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))