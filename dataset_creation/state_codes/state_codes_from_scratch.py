import requests
from bs4 import BeautifulSoup
import datetime
import random
import numpy as np
import lzma as xz
import json

# The other file was run to grab the state codes. This captures
# all the states with no errors, but takes way too long to run (timing out). If
# someone has capacity to get fix the bandwidth issues on this, feel free to take a stab! 

def state_code_scrape(url_val):
	page = requests.get(url_val)
	soup = BeautifulSoup(page.content, "html.parser")
	results = soup.find(id="codes-content")
	return results.text

def year_list_scrape(url_val):
	page = requests.get(url_val)
	soup = BeautifulSoup(page.content, "html.parser")
	results = soup.find(id="main-content")
	code_years = results.find("ul")
	year_list = [year.text[:4] for year in code_years]
	return year_list

# saving the train / val files
def save_final_data(state_json_data, final_path):
	with xz.open(final_path, 'w') as state_data:
		for state_doc in state_json_data:
			state_data.write((json.dumps(state_doc) + "\n").encode("utf-8"))

def create_nested_doc(url_val, base_url):
	final_text = ""
	page = requests.get(url_val)
	soup = BeautifulSoup(page.content, "html.parser")
	title_sections = soup.find("div", class_="codes-listing")
	if title_sections == None:
		return state_code_scrape(url_val)
	else:
		title_section = title_sections.find_all("li")
		for sec in title_section:
			final_link = ""
			further_sec = sec.find_all('a', href=True)
			for l in further_sec:
				final_link = l['href']
			if final_link != "":
				sec_url = base_url + final_link
				final_text += create_nested_doc(sec_url, base_url)
	return final_text

state_names = ["Alaska", "Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut", "District-of-columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North-carolina", "North-dakota", "Nebraska", "New-hampshire", "New-jersey", "New-mexico", "Nevada", "New-york", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto-rico", "Rhode-island", "South-carolina", "South-dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin-Islands", "Vermont", "Washington", "Wisconsin", "West-virginia", "Wyoming"]
state_names = [x.lower() for x in state_names]

base_url = "https://law.justia.com"
docs = []
for state in state_names:
	state_base_url = base_url + '/codes/' + state
	year_list = year_list_scrape(state_base_url)
	for year in year_list:
		constructed_doc = ""
		year_url = state_base_url + '/' + year
		constructed_doc = create_nested_doc(year_url, base_url)
		docs.append({
		"url" : year_url, #TODO how to pull google drive links
		"text" : constructed_doc,
		"downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
		"created_timestamp" : "",
		"state_year": state + '_' + year
		})
		print(constructed_doc)

# train / test split from process_tax_corpus_jhu.py
random.seed(0)
rand_idx = list(range(len(docs)))
random.shuffle(rand_idx)

train_idx = rand_idx[:int(len(rand_idx)*0.75)]
val_idx = rand_idx[int(len(rand_idx)*0.75):]

train_docs = np.array(docs)[train_idx]
val_docs = np.array(docs)[val_idx]

# saving data 
save_final_data(train_docs, "train.state_codes.jsonl.xz")
save_final_data(val_docs, "validation.state_codes.jsonl.xz")









