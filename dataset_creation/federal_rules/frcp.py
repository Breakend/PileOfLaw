import requests
from bs4 import BeautifulSoup
import datetime
import random
import numpy as np
import lzma as xz
import json

def scrape_rule(url_val):
	page = requests.get(url_val)
	soup = BeautifulSoup(page.content, "html.parser")
	rule_content = soup.find(id="content1")
	if rule_content == None:
		return ""
	remove_text = rule_content.find(id="book-navigation-4940065")
	add_title = soup.find(id="page-title")
	# removing the bottom navigation titles that get scraped with the rule body
	stop_idx = rule_content.text.find(remove_text.text)
	# appending the name and editd rule content
	final_rule = add_title.text + rule_content.text[:stop_idx].strip()
	return final_rule

# saving the train / val files
def save_final_data(state_json_data, final_path):
	with xz.open(final_path, 'w') as state_data:
		for state_doc in state_json_data:
			state_data.write((json.dumps(state_doc) + "\n").encode("utf-8"))

basic_url_val = "https://www.law.cornell.edu/rules/frcp/rule_"
rule_idx = [str(x + 1) for x in list(range(86))]
rule_idx.extend(["A", "B", "C", "D", "E", "F", "G"])

# get the number of rules in an article
docs = []
for rule in rule_idx:
	full_rule_url = basic_url_val + rule
	rule_content = scrape_rule(full_rule_url)
	if rule_content == "":
		continue
	docs.append({
		"url" : full_rule_url,
		"text" : rule_content,
		"downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
		"created_timestamp" : ""
		})

# train / test split from process_tax_corpus_jhu.py
random.seed(0)
rand_idx = list(range(len(docs)))
random.shuffle(rand_idx)

train_idx = rand_idx[:int(len(rand_idx)*0.75)]
val_idx = rand_idx[int(len(rand_idx)*0.75):]

train_docs = np.array(docs)[train_idx]
val_docs = np.array(docs)[val_idx]

# saving data 
save_final_data(train_docs, "train.frcp.jsonl.xz")
save_final_data(val_docs, "validation.frcp.jsonl.xz")







