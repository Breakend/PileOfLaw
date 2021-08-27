# Processes TOS XML files.
# XML with annotation tags (clause type / whether clause is unfair) can be downloaded from: http://claudette.eui.eu/ToS.zip
# XML files located in  OriginalTaggedDocuments subdirectory

import os
import json
import re
import random
import numpy as np
import datetime
from tqdm import tqdm
from dateutil import parser
from bs4 import BeautifulSoup

# FILE PATHS
RAW_PATH = "../../data/tos/raw" # path to contracts
OUT_PATH = "../../data/tos/processed" # path to write data (docs of original text) out to
OUT_PATH_TAGGED = "../../data/tos/processed_tagged" # path to write data (docs of original text with annotation tags) out to

# Regex match for date
match_text_patterns = ["Last Updated Date:", "Last Updated:", "Last updated:", "last updated on", "Last revised on", "Last Revised:", "Last revised on", "Revised", "Date of Last Revision:", "Last modified:", "Last modified by", "in effect as of", "Effective Date:", "Effective:", "effective on", "Effective on", "Applicable from:"]
combined_text_regex = '(?:%s)' % '|'.join(match_text_patterns)

match_date_patterns = [
	r'(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{1,2}(th)?,\s+\d{4}',
	r'\d{1,2}\s+(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)(,)?\s+\d{4}',
	r'\d{1,2}/\d{1,2}/\d{4}',
	r'\d{4}-\d{1,2}-\d{1,2}'
]
combined_date_regex = '(?:%s)' % '|'.join(match_date_patterns)

def save_to_processed(train, val, source_name, out_path):
	if not os.path.exists(out_path):
		os.makedirs(out_path)
	tf = os.path.join(out_path, f"train.{source_name}.jsonl")
	with open(tf, mode='w', encoding='utf-8') as out_file:
		for line in train:
			out_file.write(json.dumps(line) + "\n")
	print(f"Written {len(train)} documents to {tf}")

	vf = os.path.join(out_path, f"validation.{source_name}.jsonl")
	with open(vf, mode='w', encoding='utf-8') as out_file:
		for line in val:
			out_file.write(json.dumps(line) + "\n")
	print(f"Written {len(val)} documents to {vf}")

def main():
	files = [os.path.join(RAW_PATH, f) for f in os.listdir(RAW_PATH)]
	print(f"{len(files)} total documents.")
	outputs = []
	outputs_tagged = []
	for file in tqdm(files):
		print("Processing:", file)
		with open(file, mode='r', encoding='utf-8') as in_file:
			text_tagged = in_file.read()

			# Remove annotation tags
			soup = BeautifulSoup(text_tagged, features="lxml")
			text = soup.get_text()

			# Extract creation date
			lines = text.splitlines()
			date_text = None
			for line in lines:
				date_text = re.search(combined_text_regex, line)
				# If matched text describing date, break at current line
				if date_text:
					break
			creation_date = ""
			if date_text:
				match = re.search(combined_date_regex, line)
				# If matched date, parse match
				if match:
					creation_date = parser.parse(match.group()).strftime("%m-%d-%Y")

			outputs.append({
				"url": "http://claudette.eui.eu/ToS.zip",
				"created_timestamp": creation_date,
				"downloaded_timestamp": datetime.date.today().strftime("%m-%d-%Y"),
				"text": text
			})

			outputs_tagged.append({
				"url": "http://claudette.eui.eu/ToS.zip",
				"created_timestamp": creation_date,
				"downloaded_timestamp": datetime.date.today().strftime("%m-%d-%Y"),
				"text": text_tagged
			})

	outputs = np.array(outputs)
	outputs_tagged = np.array(outputs_tagged)

	random.seed(0) # important for shuffling
	rand_idx = list(range(len(outputs)))
	random.shuffle(rand_idx)

	train_idx = rand_idx[:int(len(rand_idx)*0.75)]
	val_idx = rand_idx[int(len(rand_idx)*0.75):]

	# Same split for docs of original text and original text with annotation tags
	train = outputs[train_idx]
	val = outputs[val_idx]

	train_tagged = outputs_tagged[train_idx]
	val_tagged = outputs_tagged[val_idx]

	# Save train / val to processed
	save_to_processed(train, val, "tos", OUT_PATH)

	# Save train_tagged / val_tagged to processed_tagged
	save_to_processed(train_tagged, val_tagged, "tos_tagged", OUT_PATH_TAGGED)

if __name__ == "__main__":
	main()