import glob
import os
import json
try:
	import lzma as xz
except ImportError:
	import pylzma as xz
import scrubadub
from tqdm import tqdm

# DATA DIRS
IN_DIR = 'data'
OUT_DIR = 'data_scrubbed'
FILTH_DIR = 'filth'

# remaining 
TO_SCRUB = ['train.atticus_contracts.jsonl.xz',
			'validation.atticus_contracts.jsonl.xz',
			'train.bva.jsonl.xz',
			'validation.bva.jsonl.xz',
			'train.congressional_hearings.xz',
			'validation.congressional_hearings.xz',
			'train.courtlistenerdocketentries.xz',
			'validation.courtlistenerdocketentries.xz',
			'train.courtlisteneropinions.xz',
			'validation.courtlisteneropinions.xz',
			'train.edgar.jsonl.xz',
			'validation.edgar.jsonl.xz',
			]


def scrub(filepath, scrubber):
		"""This function scrubs the data file of sensitive information.
			Returns
				- A list of the documents in the data file, with text scrubbed
				- A dict of the file filth data
		"""
		print(f"Scrub {filepath}")

		print(f"Read {filepath}")
		lines = []
		with xz.open(filepath, mode='rb') as f:
			while True:
				try:
					line = f.readline().decode('utf-8')
					if line == "":
						break
					lines.append(line)
				except:
					print("corrupted line")
					break


		print(f"Clean {filepath}")
		docs_scrubbed = []
		docs_filth_data = []

		filth_count = 0
		word_count = 0
		filth_doc_count = 0

		for line in tqdm(lines):
			if line is not None and line != "":
				doc = json.loads(line)
				doc_text = doc["text"]
				doc_word_count = len(doc_text.split())
				word_count += doc_word_count

				# Detect filth
				filth_objs = list(scrubber.iter_filth(doc_text))
				doc_filth_count = len(filth_objs)
				filth_count += doc_filth_count
				if doc_filth_count > 0:
					filth_doc_count += 1

				doc_filth = []
				for filth_obj in filth_objs:
					filth = {}
					if isinstance(filth_obj, scrubadub.filth.base.MergedFilth): # filth_obj is MergedFilth
						types = []
						texts = []
						for filth_obj_i in filth_obj.filths:
							types.append(filth_obj_i.detector_name)
							texts.append(filth_obj_i.text)
						filth["type"] = types
						filth["text"] = texts
						filth["merged_text"] = filth_obj.text
						filth["merged"] = True
					else: # filth_obj is Filth
						filth["type"] = filth_obj.detector_name
						filth["text"] = filth_obj.text
						filth["merged"] = False
					doc_filth.append(filth)

				doc_filth_data = {}
				doc_filth_data["url"] = doc["url"]
				doc_filth_data["filth_count"] = doc_filth_count
				doc_filth_data["word_count"] = doc_word_count
				doc_filth_data["filth"] = doc_filth

				# Clean
				cleaned_text = scrubber.clean(doc_text)
				doc["text"] = cleaned_text

				docs_scrubbed.append(doc)
				docs_filth_data.append(doc_filth_data)

		file_filth_data = {}
		file_filth_data["filename"] = filepath.split('/')[-1]
		file_filth_data["filth_count"] = filth_count
		file_filth_data["word_count"] = word_count
		file_filth_data["filth_doc_count"] = filth_doc_count
		file_filth_data["doc_count"] = len(lines)
		file_filth_data["filth_data"] = docs_filth_data

		return docs_scrubbed, file_filth_data


def init_scrubber():
	"""Initialize scrubber with detectors."""
	detector_list = [scrubadub.detectors.en_US.SocialSecurityNumberDetector,
					 scrubadub.detectors.PhoneDetector,
					 scrubadub.detectors.EmailDetector,
					 scrubadub.detectors.CreditCardDetector
					]
	scrubber = scrubadub.Scrubber(detector_list=detector_list, locale='en_US')
	return scrubber


def save_compressed_file(data, out_dir, filename):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
	filepath = os.path.join(out_dir, filename)
	with xz.open(filepath, 'w') as out_file:
		for x in data:
			out_file.write((json.dumps(x) + "\n").encode("utf-8"))


def save_json_file(data, out_dir, filename):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
	filepath = os.path.join(out_dir, filename)
	with open(filepath, 'w') as out_file:
		json.dump(data, out_file)


def main():
	filepaths_all = glob.glob(os.path.join(IN_DIR, "*.xz"))
	filepaths_to_scrub = [filepath for filepath in filepaths_all if filepath.split('/')[-1] in TO_SCRUB]

	scrubber = init_scrubber()
	for filepath in filepaths_to_scrub:
		docs_scrubbed, filth_data = scrub(filepath, scrubber)

		filename = filepath.split('/')[-1]
		trunc_filename = ".".join(filename.split('.')[0:2])

		# Save cleaned docs as compressed xz file
		save_compressed_file(docs_scrubbed, OUT_DIR, filename)

		# Save file filth data to json
		save_json_file(filth_data, FILTH_DIR, trunc_filename + ".json")


if __name__ == '__main__':
	main()