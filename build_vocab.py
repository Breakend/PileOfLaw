# This script builds vocab
import argparse
import glob
import os
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers import normalizers, pre_tokenizers
import ujson

try:
    import lzma as xz
except ImportError:
    import pylzma as xz

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--hf_dataset', action='store_true',
                    help='Whether to build from hugging face dataset. Otherwise, builds from raw files')
parser.add_argument('--raw_data', default='raw_data', help='path to raw data')


def build_from_raw(args):
    path = os.path.join(args.raw_data, "*.xz")
    files = glob.glob(path)
    print(f"Found {len(files)} files.")
    def xz_iterator():
        for path in files:
            try:
                with xz.open(path) as f:
                    for line in f:
                        obj = ujson.loads(line)
                        if not obj is None and 'text' in obj:
                            yield ['text']
                        else:
                            yield ""
            except xz.LZMAError as e:
                print(f"Error {e} with {path}. Skipping.")
            except Exception as e:
                print(f"Error {e} with {path}. Skipping.")

    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    trainer = BpeTrainer(
        special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
        vocab_size=1000,
        show_progress=True
    )
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel()
    tokenizer.normalizer = normalizers.BertNormalizer()
    tokenizer.train_from_iterator(xz_iterator(), trainer=trainer)

    tokenizer.save("vocab.json")


if __name__ == '__main__':
    args = parser.parse_args()
    build_from_raw(args)