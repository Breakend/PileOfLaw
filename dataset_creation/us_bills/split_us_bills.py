# Loads data files saved by session (108th-117th Congress) from the bulk data API endpoints
# Splits all data into train / test data

import os
import glob
import json
import random
from process_us_bills import save_to_file

# DATA DIRS
SAVE_DIR = "../../data/us_bills/save" # path to save per session data
OUT_DIR = "../../data/us_bills/processed" # path to write data out to

def main():
	docs = []
	# Load all sessions from saved per-session data files
	session_files = glob.glob(os.path.join(SAVE_DIR, "*.jsonl"))
	for session_file in session_files:
		print(session_file)
		with open(session_file, 'r') as file:
			for line in file:
				docs.append(json.loads(line))

	# Shuffle and split into train / validation
	random.seed(0)
	random.shuffle(docs)
	train = docs[:int(len(docs)*0.75)]
	validation = docs[int(len(docs)*0.75):]

	print("Write train data")
	save_to_file(train, OUT_DIR, "train.us_bills.jsonl")
	print("Write validation data")
	save_to_file(validation, OUT_DIR, "validation.us_bills.jsonl")


if __name__ == '__main__':
	main()