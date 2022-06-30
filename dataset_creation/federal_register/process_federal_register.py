# Processes federal register proposed rules (2000 - 2021)
# Bulk data pulled from: https://www.govinfo.gov/bulkdata/xml/FR

import os
import json
import datetime
import random
from urllib.request import Request, urlopen
# xpath only available in lxml etree, not ElementTree
from lxml import etree
from tqdm import tqdm
from dateutil import parser

# BASE URL (bulk data API endpoint)
BASE_URL = "https://www.govinfo.gov/bulkdata/xml/FR"

# DATA DIRS
OUT_DIR = "../../data/federal_register/processed" # path to write data out to

# Request variables
headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/xml'}


def save_to_file(data, out_dir, fname):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
	fpath = os.path.join(out_dir, fname)
	with open(fpath, 'w') as out_file:
		for x in data:
			out_file.write(json.dumps(x) + "\n")
	print(f"Written {len(data)} to {fpath}")


def request_raw_data():
	urls = [BASE_URL]
	xmls = []
	while len(urls) > 0:
		next_urls = []
		for url in urls:
			print(url)
			request = Request(url, headers=headers)
			with urlopen(request) as response:
				root = etree.fromstring(response.read())
			elems = root.xpath("*/file[folder='true' and name!='resources']")
			if len(elems) > 0:
				for e in elems:
					next_url = e.find("link").text
					next_urls.append(next_url)
			else:
				elems = root.xpath("*/file[mimeType='application/xml']")
				for e in elems:
					xml_url = e.find("link").text
					request = Request(xml_url, headers=headers)
					with urlopen(request) as response:
						xml = etree.fromstring(response.read())
					# Add tuple of xml_url, xml Element instance
					xmls.append((xml_url, xml))
		urls = next_urls

	return xmls

def extract_rule_docs(xmls):
	docs = []
	for (xml_url, xml) in tqdm(xmls):
		print(xml_url)
		date = xml.find("DATE").text
		creation_date = ""
		try:
			creation_date = parser.parse(date).strftime("%m-%d-%Y")
		except:
			pass

		proposed_rules = xml.xpath("PRORULES/PRORULE")
		for rule in proposed_rules:
			# In Python 3, use encoding='unicode'
			# In Python 2, use encoding='utf-8' and decode
			all_text = etree.tostring(rule, encoding='unicode', method='text')

		doc = {
			"url": xml_url,
			"created_timestamp": creation_date,
			"downloaded_timestamp": datetime.date.today().strftime("%m-%d-%Y"),
			"text": all_text
		}
		docs.append(doc)

	return docs


def main():
	# Request raw data directly using bulk data API
	xmls = request_raw_data()
	docs = extract_rule_docs(xmls)

	# Shuffle and split into train / validation
	random.seed(0)
	random.shuffle(docs)
	train = docs[:int(len(docs)*0.75)]
	validation = docs[int(len(docs)*0.75):]

	save_to_file(train, OUT_DIR, "train.federal_register.jsonl")
	save_to_file(validation, OUT_DIR, "validation.federal_register.jsonl")


if __name__ == '__main__':
	main()