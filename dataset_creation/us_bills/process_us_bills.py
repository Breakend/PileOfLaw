# Processes US congressional bills from the 108th - 117th Congress
# Bulk data pulled from: https://www.govinfo.gov/bulkdata/xml/BILLSTATUS
# Requests to bulk data API endpoint are prone to request errors, 
# use run.sh to call this script for each session for greater fault tolerance

import os
import sys
import json
import datetime
import random
from urllib.request import Request, urlopen
# xpath only available in lxml etree, not ElementTree
from lxml import etree
from tqdm import tqdm
from dateutil import parser
import time
import argparse

# BASE URL (bulk data API endpoint)
BASE_URL = "https://www.govinfo.gov/bulkdata/xml/BILLSTATUS"

# DATA DIRS
SAVE_DIR = "../../data/us_bills/save" # path to save per session data

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


def request_status_xmls(session):
	urls = [os.path.join(BASE_URL, str(session))]
	status_xmls = []
	while len(urls) > 0:
		next_urls = []
		for url in urls:
			print(url)
			request = Request(url, headers=headers)
			time.sleep(random.uniform(0.02, 0.05))
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
					# print(xml_url)
					request = Request(xml_url, headers=headers)
					for i in range(3): # retry request max of 3 times
						try:
							time.sleep(random.uniform(0.02, 0.05))
							with urlopen(request) as response:
								xml = etree.fromstring(response.read())
							# Add xml for bill status
							status_xmls.append(xml)
							break
						except:
							print("Retrying")

		urls = next_urls

	return status_xmls


def request_raw_data(status_xmls):
	xmls = []
	for status_xml in tqdm(status_xmls):
		# print(status_xml)
		# Text versions are sorted in date order, find returns first item, which is most recent version
		text_info = status_xml.find("bill/textVersions/item")
		if text_info is not None:
			try:
				date = text_info.find("date").text
			except:
				date = ""
			try:
				xml_url = text_info.find("formats/item/url").text
			except:
				xml_url = None
			if xml_url:
				request = Request(xml_url, headers=headers)
				for i in range(3):
					try:
						time.sleep(random.uniform(0.02, 0.05))
						with urlopen(request) as response:
							xml = etree.fromstring(response.read())
						# print(date, xml_url)
						# Add tuple of (date, xml_url, xml) for raw bill text
						xmls.append((date, xml_url, xml))
						break
					except:
						print("Retrying")

	return xmls


def prepare_docs(xmls):
	docs = []
	for (date, xml_url, xml) in tqdm(xmls):
		try:
			creation_date = parser.parse(date).strftime("%m-%d-%Y")
		except:
			creation_date = ""

		# In Python 3, use encoding='unicode'
		# In Python 2, use encoding='utf-8' and decode
		all_text = etree.tostring(xml, encoding='unicode', method='text')

		doc = {
			"url": xml_url,
			"created_timestamp": creation_date,
			"downloaded_timestamp": datetime.date.today().strftime("%m-%d-%Y"),
			"text": all_text
		}
		docs.append(doc)

	return docs


def main():
	args = arg_parser.parse_args()

	# Request raw data directly using bulk data API
	print("Request status xmls")
	status_xmls = request_status_xmls(session=args.session)
	print("Request raw data")
	xmls = request_raw_data(status_xmls)
	print("Prepare docs")
	docs = prepare_docs(xmls)

	save_to_file(docs, SAVE_DIR, str(args.session) + ".us_bills.jsonl")


if __name__ == '__main__':
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument('--session', type=int, default=117)
	main()