import argparse
import requests
import re
from tqdm import tqdm 
import wget
import os
import json
import PyPDF2 
import glob
import datetime
import random

from multiprocessing import Pool


DIR = "../data/nlrb/scraping"
OUT_DIR = "../data/nlrb/processed"
BASE_URL = "https://www.nlrb.gov/cases-decisions/decisions/board-decisions?search_term=&op=Search&volume=-1&slip_opinion_number=&page_number=$PAGE_NUMBER&items_per_page=100&form_build_id=form-EXFTGMwfIM0yO2L6ENa30_RuqwbWvmk5YR1UYcvgqsA&form_id=board_decisions_form"


def get_urls(args):
    all_matches = []
    for page_num in tqdm(range(661)):
        url = BASE_URL.replace("$PAGE_NUMBER", str(page_num))
        page = requests.get(url)
        text = page.text
        #p = re.compile("href=\"(https\:\/\/apps\.nlrb\.gov\/link\/document\.aspx\/[a-z0-9]*)\"")
        p = re.compile("< td > ([0 - 9] *\ /[0-9] * \ /[0-9] *) <\ / td >\s * < td > [0 - 9] * NLRB No\.[0 - 9] * <\ / td >\s * < td >\s * < a href =\"(https\:\/\/apps\.nlrb\.gov\/link\/document\.aspx\/[a-z0-9]*)\"")
        all_matches.extend(re.findall(p, text))
        break
    
    # save to file 
    out_fpath = os.path.join(DIR, "urls.txt")
    with open(out_fpath, "w") as out_file:
        out_file.write(json.dumps(all_matches))

def download_pdf(url):
    out = os.path.join(DIR, "pdfs")
    out = os.path.join(out, url.split("/")[-1] + ".pdf")
    if os.path.exists(out):
        return
    filename = wget.download(url, out=out, bar = False)

def download_pdfs(args):
    url_fpath = os.path.join(DIR, "urls.txt")
    urls = json.load(open(url_fpath))
    urls = urls
    with Pool(20) as p:
      r = list(tqdm(p.imap(download_pdf, urls), total=len(urls)))
    

def convert_pdf(fpath):
    text = ""
    # creating a pdf file object 
    pdfFileObj = open(fpath, 'rb') 
        
    # creating a pdf reader object 
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
        
    # printing number of pages in pdf file 
    for page in range(pdfReader.numPages):
        
        # creating a page object 
        pageObj = pdfReader.getPage(page) 

        try:
            # extracting text from page 
            text = text + " " + pageObj.extractText()
        except:
            pass

    # closing the pdf file object 
    pdfFileObj.close()  
    return text 

def convert_pdfs_to_text(args):
    fdir = os.path.join(DIR, "pdfs", "*.pdf")
    pdf_files = glob.glob(fdir)

    for f in tqdm(pdf_files):
        if "(1)" in f:
            continue
        out_fpath = os.path.join(DIR, "text", f.split("/")[-1].replace(".pdf", ".txt"))
        if os.path.exists(out_fpath):
            continue
        try:
            text = convert_pdf(f)
        except:
            text = ""
        if len(text) == 0:
            continue
        with open(out_fpath, "w") as outf:
            outf.write(text)

def save_to_file(data, fpath):
    with open(fpath, "w") as out_file:
        for x in data:
            out_file.write(json.dumps(x) + "\n")
    print(f"Written {len(data)} to {fpath}")

def create_splits(args):
    # load contracts 
    files = glob.glob(os.path.join(DIR, "text", "*.txt"))
    print(f"Collected {len(files)} decisions.")
    docs = []
    for f in tqdm(files): 
        text = ""
        with open(f) as in_file: 
            for line in in_file:
                text = text + line
        
        doc = {
            "url": "https://www.nlrb.gov/cases-decisions/decisions/board-decisions",
            "created_timestamp": "",
            "timestamp": datetime.date.today().strftime("%m-%d-%Y"),
            "text": text
        }
        docs.append(doc) 
    
    # shuffle and split into train / validation 
    random.seed(0)
    random.shuffle(docs)
    train = docs[:int(len(docs)*0.75)]
    validation = docs[int(len(docs)*0.75):]

    save_to_file(train, os.path.join(OUT_DIR, "train.nlrb_decisions.jsonl"))
    save_to_file(validation, os.path.join(OUT_DIR, "validation.nlrb_decisions.jsonl"))
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--get_urls', action='store_true',
                        help='Aggregates URLS of PDFs from NLRB website')
    parser.add_argument('--download_pdfs', action='store_true',
                        help='Downloads PDFS')
    parser.add_argument('--convert_pdfs', action='store_true',
                        help='Converts PDF files to text files')
    parser.add_argument('--create_splits', action='store_true',
                        help='Aggregates text files into train / val jsonls')

    args = parser.parse_args()
    if args.get_urls:
        get_urls(args)
    if args.download_pdfs:
        download_pdfs(args)
    if args.convert_pdfs:
        convert_pdfs_to_text(args)
    if args.create_splits:
        create_splits(args)
    #main()