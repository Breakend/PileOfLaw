import glob
import os
import json
import lzma as xz
import tarfile
import scrubadub
import pickle
from tqdm import tqdm

# DATA DIRS
IN_DIR = 'data'
OUT_DIR = 'data_scrubbed'
FILTH_DIR = 'filth'

def scrub(filepath, scrubber):
		"""This function scrubs the data file of sensitive information."""
		print(f"Scrub {filepath}")

		docs_scrubbed = []
		docs_filth = []

		with xz.open(filepath, mode='rb') as f:
			print(f"Read {filepath}")
			lines = []
			while True:
				try:
					line = f.readline()
					lines.append(line)
					if line == "":
						break
				except:
					print("corrupted line")
					break


			print(f"Clean {filepath}")
			for line in tqdm(lines):
				if line is not None and line != "":
					doc = json.loads(line)
					text = doc["text"]

					# Detect filth
					filth = list(scrubber.iter_filth(text))
					filth = [(item.detector_name, item.text) for item in filth]

					# Clean
					cleaned_text = scrubber.clean(text)
					doc["text"] = cleaned_text
				
					docs_scrubbed.append(doc)
					docs_filth.append(filth)

		return docs_scrubbed, docs_filth


def init_scrubber():
	"""Initialize scrubber with detectors."""
	detector_list = [scrubadub.detectors.en_US.SocialSecurityNumberDetector,
					 scrubadub.detectors.PhoneDetector,
					 scrubadub.detectors.EmailDetector,
					 scrubadub.detectors.CreditCardDetector
					]
	scrubber = scrubadub.Scrubber(detector_list=detector_list, locale='en_US')
	return scrubber


def save_to_file(data, out_dir, fname):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
	fpath = os.path.join(out_dir, fname)
	with open(fpath, 'w') as out_file:
		for x in data:
			out_file.write(json.dumps(x) + "\n")
	print(f"Written {len(data)} to {fpath}")


def save_pickle(data, out_dir, fname):
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)
	fpath = os.path.join(out_dir, fname)
	with open(fpath, 'wb') as out_file:
		pickle.dump(data, out_file)


def main():
	filepaths = glob.glob(os.path.join(IN_DIR, "*.xz"))

	scrubber = init_scrubber()
	for filepath in filepaths:
		docs_scrubbed, docs_filth = scrub(filepath, scrubber)

		fname = '.'.join((filepath.split('/')[-1]).split('.')[0:-1])

		# Save cleaned docs as jsonl
		save_to_file(docs_scrubbed, OUT_DIR, fname)

		# Pickle doc filth as a list of lists (filth list per doc)
		save_pickle(docs_filth, FILTH_DIR, fname + ".pkl")


if __name__ == '__main__':
	main()