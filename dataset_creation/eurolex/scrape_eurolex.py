import pandas as pd
import random
import json
import datetime
try:
    import lzma as xz
except ImportError:
    import pylzma as xz

lex = pd.read_csv("./cache/EurLex_all.csv")

overwrite = True
open_type = 'w' if overwrite else 'a'
train_f = xz.open("./cache/train.eurlex.xz", open_type)
val_f = xz.open("./cache/validation.eurlex.xz", open_type)

for act_name, Act_type, subject_matter, date_publication, text  in zip(lex["Act_name"], lex["Act_type"], lex["Subject_matter"], lex["Date_publication"], lex["act_raw_text"]):

    datapoint = {
        "text" : f"Name: {act_name}\n Type: {Act_type}\n Subject Matter: {subject_matter}\n Date Published: {date_publication}\n\n {text}",
        "created_timestamp" : date_publication,
        "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),
        "url" : "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/0EGYWY"
    }
    if random.random() > .75:
        val_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))
    else:
        train_f.write((json.dumps(datapoint) + "\n").encode("utf-8"))