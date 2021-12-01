# This script builds vocab
import argparse
import glob
import os
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers import normalizers, pre_tokenizers
import ujson
import random
try:
    import lzma as xz
except ImportError:
    import pylzma as xz

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--hf_dataset', action='store_true',
                    help='Whether to build from hugging face dataset. Otherwise, builds from raw files')
parser.add_argument('--raw_data', default='raw_data', help='path to raw data')
parser.add_argument('--perc', default=0.1, help='percent of data to train tokenizer on')


def build_from_raw(args):
    path = os.path.join(args.raw_data, "*.xz")
    files = glob.glob(path)
    print(f"Found {len(files)} files.")
    def xz_iterator():
        for i, path in enumerate(files):
            print(f"{i+1}/{len(files)}: {path}.")
            try:
                with xz.open(path) as f:
                    for line in f:
                        if random.random() > args.perc:
                            continue
                        obj = ujson.loads(line.strip())
                        if not obj is None and 'text' in obj:
                            yield obj['text']
                        else:
                            yield ""
            except xz.LZMAError as e:
                print(f"Error {e} with {path}. Skipping.")
            except Exception as e:
                print(f"Error {e} with {path}. Skipping.")

    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    trainer = BpeTrainer(
        special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
        vocab_size=31000,
        show_progress=True
    )
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel()
    tokenizer.normalizer = normalizers.BertNormalizer()
    tokenizer.train_from_iterator(xz_iterator(), trainer=trainer, length=133521688)

    #tokenizer.save_model("vocab_params.json")
    #print(f"Vocab size: {tokenizer.get_vocab_size()}")
    #print(tokenizer.get_vocab())
    out_dir = f"vocab_{args.perc:.2f}"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    tokenizer.model.save(out_dir)


if __name__ == '__main__':
    args = parser.parse_args()
    build_from_raw(args)