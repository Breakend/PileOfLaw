import datetime

import scrapelib
import pytz
import os
import cachetools
import textract
import numpy as np
import random
import json
import requests_cache
try:
    import lzma as xz
except ImportError:
    import pylzma as xz

requests = requests_cache.CachedSession('casebriefscache')
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
headers['X-Api-Key'] = os.environ['API_KEY']

class GovInfo(scrapelib.Scraper):
    BASE_URL = 'https://api.govinfo.gov'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(os.environ['API_KEY'])
        self.headers['X-Api-Key'] = os.environ['API_KEY']


    def collections(self):
        endpoint = '/collections'
        response = requests.get(self.BASE_URL + endpoint, headers=headers)
        return response.json()


    def _format_time(self, dt):

        utc_time = dt.astimezone(pytz.utc)
        time_str = dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        return time_str

    def congressional_hearings(self, congress=117):


        partial = f"/collections/CHRG/{self._format_time(datetime.datetime(1970, 1, 1, 0, 0, tzinfo=pytz.utc))}/"
        url_template = self.BASE_URL + partial 

        seen = cachetools.LRUCache(30)
        for page in self._pages(url_template, congress):
            for package in page['packages']:
                package_id = package['packageId']

                if package_id in seen:
                    continue
                else:
                    # the LRUCache is like a dict, but all we care
                    # about is whether we've seen this package
                    # recently, so we just store None as the value
                    # associated with the package_id key
                    seen[package_id] = None

                response = self.get(package['packageLink'])
                yield response.json()

    def _download_pdf(self, data):
        # if not "html" in data["download"]:
        #     print(data["download"].keys())
        #     return
        url = data["download"]["zipLink"]
        tag = url.split("/")[-2]
        url = f"https://www.govinfo.gov/content/pkg/{tag}/html/{tag}.htm"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return None

        text = str(response.content)

        # with open(f'cache/{tag}.pdf', 'wb') as f:
        #     f.write(response.content)

        # text = str(textract.process(f'cache/{tag}.pdf', method="tesseract"))

        datapoint = {
            "text" : text,
            "created_timestamp" : data['dateIssued'],
            "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
            "url" : url
        }
        return datapoint

    def _pages(self, url_template, congress):
        page_size = 100

        params = {'offset':  0,
                  'pageSize': page_size,
                  "congress" : congress}

        url =  url_template

        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        yield data

        while len(data['packages']) == page_size:

            # the API results are sorted in descending order by timestamp
            # so we can paginate through results by making the end_time
            # filter earlier and earlier
            earliest_timestamp = data['packages'][-1]['lastModified']
            url = url_template.format(end_time=earliest_timestamp)

            response = self.get(url, params=params)
            data = response.json()

            yield data


scraper = GovInfo()

# Prints out all the different types of collections available
# in the govinfo API
print(scraper.collections())

# Iterate through every congressional hearing
#
# For congressional hearings you need a specify a start
# date time with a timezone
# start_time = datetime.datetime(2020, 1, 1, 0, 0, tzinfo=pytz.utc)
congresses = np.arange(89, 118)[::-1]

seen_urls = []
with xz.open("./cache/train.congressional_hearings.xz", 'r') as f:
    seen_urls.extend([x["url"] for x in f.readlines()])
with xz.open("./cache/validation.congressional_hearings.xz", 'r') as f:
    seen_urls.extend([x["url"] for x in f.readlines()])

import pdb; pdb.set_trace()
# val_f = xz.open("./cache/validation.congressional_hearings.xz", 'r')



i = 0
overwrite = False
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.congressional_hearings.xz", open_type)
val_f = xz.open("./cache/validation.congressional_hearings.xz", open_type)
for congress in congresses:
    print(f"NOW GETTING CONGRESS {congress}")
    for hearing in scraper.congressional_hearings(congress):
        datapoint = scraper._download_pdf(hearing)
        if datapoint is None:
            print("No data for hearing")
            print(hearing)
            continue
        i += 1
        if i % 1000 == 0:
            print(i)
        # import pdb; pdb.set_trace()
        if random.random() > .75:
            val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
        else:
            train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
