
import json
import os
from tqdm import tqdm
try:
    import lzma as xz
except ImportError:
    import pylzma as xz


fdir = "data/atticus_contract/processed/"
train_in = os.path.join(fdir, "train.atticus_contracts.jsonl")
train_out = train_in + ".xz"
val_in = os.path.join(fdir, "validation.atticus_contracts.jsonl")
val_out = val_in + ".xz"


def save(inf, outfname):
    data = []
    with open(inf) as in_file:
        for line in in_file:
            data.append(line)
    outf = xz.open(outfname, "w")
    for line in tqdm(data):
        outf.write((line.strip() + "\n").encode("utf-8"))
    print(f"{inf} -> {outfname}")

save(train_in, train_out)
save(val_in, val_out)