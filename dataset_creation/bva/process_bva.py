# Processes BVA opinions (2001-2018)
# Raw txt files downloaded through private link shared by authors of this paper: https://arxiv.org/abs/2106.10776
# In the future, the files will be available here: https://drive.google.com/drive/folders/12lAd8Os7VFeqbTKi4wcqJqODjHIn0-yQ?usp=sharing

import os
import re
import glob
import json
import tarfile
import datetime
import random
from tqdm import tqdm
from dateutil import parser


# SOURCE URL
URL = "https://drive.google.com/drive/folders/12lAd8Os7VFeqbTKi4wcqJqODjHIn0-yQ?usp=sharing"

# DATA DIRS
IN_DIR = "../../data/bva/raw" # path to BVA opinion tar files by year
OUT_DIR = "../../data/bva/processed" # path to write data out to

# Regex for date match
date_regex = r'(?:\s*Decision\s+Date:\s+)(\d{1,2}/\d{1,2}/\d{1,2})'

def save_to_file(data, out_dir, fname):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
	fpath = os.path.join(out_dir, fname)
	with open(fpath, 'w') as out_file:
		for x in data:
			out_file.write(json.dumps(x) + "\n")
	print(f"Written {len(data)} to {fpath}")

def main():
	tar_files = glob.glob(os.path.join(IN_DIR, "*.tar.gz"))

	docs = []
	for tar_file in tqdm(tar_files):
		print("Processing tar file:", tar_file)
		tar = tarfile.open(tar_file, 'r:gz')
		for member in tar.getmembers():
			if ".txt" in member.name:
				f = tar.extractfile(member)
				content = f.read()
				# Original encoding is in latin1, we want to decode it as utf-8
				text = content.decode('latin1').encode('utf-8').decode('utf-8')

				# Extract creation date
				lines = text.splitlines()
				creation_date = ""
				match = None
				for line in lines:
					match = re.search(date_regex, line)
					# If matched date, break at current line and parse / reformat match
					if match:
						creation_date = parser.parse(match.group(1)).strftime("%m-%d-%Y")

				doc = {
					"url": URL,
					"created_timestamp": creation_date,
					"downloaded_timestamp": datetime.date.today().strftime("%m-%d-%Y"),
					"text": text
				}
				docs.append(doc)

	# Shuffle and split into train / validation
	random.seed(0)
	random.shuffle(docs)
	train = docs[:int(len(docs)*0.75)]
	validation = docs[int(len(docs)*0.75):]

	save_to_file(train, OUT_DIR, "train.bva.jsonl")
	save_to_file(validation, OUT_DIR, "validation.bva.jsonl")

if __name__ == '__main__':
	main()