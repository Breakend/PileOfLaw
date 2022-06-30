import json
import syntok.segmenter as segmenter
import re
import random 
try:
    import lzma as xz
except ImportError:
    import pylzma as xz

with open('../../dataset_creation/eoir/cache/train.eoir_pseudonym.jsonl', 'r') as f:
    data = [json.loads(x) for x in f.readlines()]

import spacy
from collections import Counter

import re
nlp = spacy.load("en_core_web_sm")
replacement = re.compile(r"(the )?(respondent|applicant|defendant|plaintiff|petitioner)(s)?", re.IGNORECASE)
def paragraphs(document):
    start = 0
    for token in document:
        if token.is_space and token.text.count("\n") > 1:
            yield document[start:token.i]
            start = token.i
    yield document[start:]

with xz.open("./train.privacy.eoir.jsonl.xz", "wt") as f1:
    with xz.open("./validation.privacy.eoir.jsonl.xz", "wt") as f2:
        for datapoint in data:
            doc = nlp(datapoint["text"])
            for paragraph in paragraphs(doc):
                if len(paragraph.text) < 700:
                    continue
                if ", Respondent" in paragraph.text:
                    continue
                # TODO: better paragraph splitting
                text = paragraph.text
                text = text.replace("\n", " ")

                for ent in paragraph.ents:
                    if ent.label_ == "PERSON":
                        if not ("v." in text[max(0, ent.start-5):min(ent.end + 5, len(text))].lower()) or  ("in re" in text[max(0, ent.start-5):min(ent.end + 5, len(text))].lower()):
                            swapped_para = replacement.sub("[MASK]", text)

                if "[MASK]" not in swapped_para:
                    continue
                
                print(datapoint["name"])
                new_data = {
                    "text" : swapped_para,
                    "label" : datapoint["is_pseudonym"],
                    "year" : datapoint["created_timestamp"].split(".")[-1],
                    "name" : datapoint["name"]
                }

                if random.random() < .15:
                    f2.write(json.dumps(new_data) + "\n")
                else:
                    f1.write(json.dumps(new_data) + "\n")