import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm 
import wget
import os

from multiprocessing import Pool


DIR = "../../data/nlrb/scraping"
BASE_URL = "https://www.nlrb.gov/cases-decisions/decisions/board-decisions?search_term=&op=Search&volume=-1&slip_opinion_number=&page_number=$PAGE_NUMBER&items_per_page=100&form_build_id=form-EXFTGMwfIM0yO2L6ENa30_RuqwbWvmk5YR1UYcvgqsA&form_id=board_decisions_form"

def collect_links(page_number):
    url = BASE_URL.replace("$PAGE_NUMBER", str(page_number))
    page = requests.get(url)
    text = page.text
    p = re.compile("href=\"(https\:\/\/apps\.nlrb\.gov\/link\/document\.aspx\/[a-z0-9]*)\"")
    matches = re.findall(p, text)
    return matches

def main():
    
    # collect links to download 
    
    for page_num in tqdm(range(661)):
        matches = collect_links(page_num)
    

    '''for i, url in enumerate(matches): 
        out_fpath = os.path.join(DIR, url.split("/")[-1] + ".pdf")
        filename = wget.download(url, out=out_fpath, bar=False)
        #print(f"{i+page_num*661}/{661*100}: {filename}")
        pbar.update(1)'''
    

if __name__ == "__main__":
    main()