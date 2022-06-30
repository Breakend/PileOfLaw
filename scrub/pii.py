# Detects PII
import glob
import os
import json
import numpy as np
import math
import argparse
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from tqdm import tqdm
from datasets import load_dataset
from multiprocessing import Pool, cpu_count

# DATA DIRS
DATA_URL = 'pile-of-law/pile-of-law'
LOG_DIR = 'logs/pii'

DATASETS = [
	'bar_exam_outlines',
	'fre',
	'tos',
	'ftc_advisory_opinions',
	'frcp',
	'constitutions',
	'cfpb_creditcard_contracts',
	'uscode',
	'olc_memos',
	'cc_casebooks',
	'echr',
	'federal_register',
	'un_debates',
	'euro_parl',
	'scotus_oral_arguments',
	'cfr',
	'founding_docs',
	'tax_rulings',
	'r_legaladvice',
	'eurlex',
	'us_bills',
	'nlrb_decisions',
	'canadian_decisions',
	'eoir',
	'dol_ecab',
    # > 200MB
	'oig',
	'scotus_filings',
	'state_codes',
	# > 1GB
	'congressional_hearings',
	'edgar',
	'bva_opinions',
	'courtlistener_docket_entry_documents',
	'atticus_contracts',
	'courtlistener_opinions',
]

SPLITS = ['train', 'validation']

# PII entities
ENTITIES = ["US_BANK_NUMBER", "US_DRIVER_LICENSE", "US_ITIN", "US_PASSPORT", "US_SNN", "CREDIT_CARD", "PHONE_NUMBER", "EMAIL_ADDRESS"]

# Threshold probabilities
PII_THRESHOLD_PROB = 0.5

MAX_LEN = int(1000000 / 10)

# In characters
CONTEXT_WINDOW = 20

def scrub_doc(doc):
	analyzer, anonymizer = init_presidio()

	doc_text = doc["text"]
	doc_words = doc_text.split()
	doc_word_count = len(doc_words)


	def detect_pii(doc_text):
		analyzer_results = analyzer.analyze(text=doc_text, entities=ENTITIES, language='en')
		# Filter results to those with score >= PII_THRESHOLD_PROB
		# From manual inspection, PII_THRESHOLD_PROB = 0.5 seems reasonable
		results = []
		for result in analyzer_results:
			result = result.to_dict()
			if result['score'] >= PII_THRESHOLD_PROB:
				doc_len_chars = len(doc_text)
				context = ""
				if result['start'] - CONTEXT_WINDOW < 0 and result['end'] + CONTEXT_WINDOW + 1 > doc_len_chars:
					context = doc_text[0:doc_len]
				elif result['start'] - CONTEXT_WINDOW < 0:
					context = doc_text[0:result['end'] + CONTEXT_WINDOW + 1]
				elif result['end'] + CONTEXT_WINDOW + 1 > doc_len_chars:
					context = doc_text[result['start'] - CONTEXT_WINDOW:doc_len_chars]
				else:
					context = doc_text[result['start'] - CONTEXT_WINDOW:result['end'] + CONTEXT_WINDOW + 1]
				results.append({'type': result['entity_type'], 'span': doc_text[result['start']: result['end']], 'context': context, 'start': result['start'], 'end': result['end'], 'score': result['score']})
		return results
	
	# Detect PII
	try:
		doc_pii = detect_pii(doc_text)
	except ValueError as error:
		print(error)

		n = math.ceil(len(doc_text) / MAX_LEN)
		print(n)
		chunks = [doc_text[i:i+MAX_LEN] for i in range(0, len(doc_text), MAX_LEN)]
		doc_pii = []
		for chunk in chunks:
			doc_pii_chunk = detect_pii(chunk)
			doc_pii += doc_pii_chunk

	doc_pii_count = len(doc_pii)

	# Aggregate doc log data
	doc_log_data = {}
	doc_log_data["url"] = doc["url"]
	doc_log_data["word_count"] = doc_word_count
	doc_log_data["pii_count"] = doc_pii_count
	doc_log_data["pii"] = doc_pii

	return doc_log_data


def scrub(split, name, dataset):
	docs_log_data = []

	# Global counts across the dataset
	pii_count = 0
	word_count = 0
	docs_with_pii = 0
	doc_count = 0

	results = None
	with Pool(processes=cpu_count() - 1) as p:
		results = list(tqdm(p.imap(scrub_doc, dataset), total=len(dataset)))

	for doc_log_data in results:
		word_count += doc_log_data["word_count"]
		pii_count += doc_log_data["pii_count"]
		if doc_log_data["pii_count"] > 0:
			docs_with_pii += 1
		doc_count += 1

		docs_log_data.append(doc_log_data)

	dataset_log_data = {}
	dataset_log_data["split"] = split
	dataset_log_data["name"] = name
	dataset_log_data["pii_count"] = pii_count
	dataset_log_data["word_count"] = word_count
	dataset_log_data["docs_with_pii"] = docs_with_pii
	dataset_log_data["doc_count"] = doc_count
	dataset_log_data["per_doc_log_data"] = docs_log_data

	return dataset_log_data


def init_presidio():
	analyzer = AnalyzerEngine()
	anonymizer = AnonymizerEngine()
	return analyzer, anonymizer


def save_json_file(data, out_dir, filename):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
	filepath = os.path.join(out_dir, filename)
	with open(filepath, 'w') as out_file:
		json.dump(data, out_file)


def main(args):
	split = args.split
	name = args.name
	print(f"{split}.{name}")
	dataset = load_dataset(DATA_URL, args.name, use_auth_token=True, split=args.split, streaming=False)
	dataset_log_data = scrub(split, name, dataset)

	# Save dataset log data (statistics on PII) to json
	save_json_file(dataset_log_data, LOG_DIR, f'{split}.{name}.json')


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--split")
	parser.add_argument("--name")
	args = parser.parse_args()
	main(args)
