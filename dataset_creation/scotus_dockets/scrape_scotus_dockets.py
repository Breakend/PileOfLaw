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
url_template_default = "https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/{year}-{n}.html"
aurl_template = "https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/{year}A{n}.html"


overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.scotus_docket_entries.xz", open_type)
val_f = xz.open("./cache/validation.scotus_docket_entries.xz", open_type)

for year in list(range(18, 22))[::-1]:

    start_ns = [0, 5001, "A"]
    # print(year)
    # if year == 21:
    #     vals = list(range(1,558)) + list(range(5001))
    # elif year == 20:
    #     vals = range(1, 8478)
    # elif year == 19:
    #     vals = range(1, 8930)
    # elif year == 18:
    #     vals = range(1, 9849)
    # else:
    #     raise ValueError("blerg")

    for start_n in start_ns:
        if start_n == "A":
            start_n = 0
            url_template = aurl_template
        else:
            url_template = url_template_default

        no_link_count = 0
        for n in range(start_n, start_n+5000):
            url = url_template.format(year=year, n=n)
            response = requests.get(url, headers=headers)
            soup= BeautifulSoup(response.text, "html.parser")     
            potential_links = soup.select("a[href$='.pdf']")
            # import pdb; pdb.set_trace()
            potential_links = [link for link in potential_links if "DocketPDF" in link["href"]]
            
            if len(potential_links) == 0:
                print(f"SKipping for year {year} at n {n} because no pdf links")
                no_link_count += 1
                if no_link_count <= 10:
                    continue
                else:
                    break
            
            no_link_count = 0

            for link in potential_links:
                try:
                    response = requests.get(link["href"], headers=headers)
                except:
                    print(f"PROBLEM GETTING {link}")
                    time.sleep(random.random()*5)
                    continue

                if not response.from_cache:
                    time.sleep(random.random()*2.)

                filepath = f'{cache}/{link["href"].split("/")[-1]}'
                if len(filepath) > 200:
                    import uuid
                    filepath = f'{cache}/{str(uuid.uuid4())}'

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                try:
                    text = str(textract.process(filepath))
                except:
                    print(f"Problem with {link['href']}")
                    continue
                if len(text) < len('\\x0c\\x0c') * 2:
                    try:
                        text = str(textract.process(filepath, method='tesseract'))
                    except:
                        print(f"Problem with {link['href']}")
                        continue
                if len(text) < len('\\x0c\\x0c') * 2:
                    continue 
                    
                os.remove(filepath)
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