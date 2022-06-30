# !pip install tokenizers
import os
from tokenizers import BertWordPieceTokenizer

fileList = [os.path.join("./unzipped_nojson", x) for x in os.listdir("./unzipped_nojson") if x is not None]

# initialize
tokenizer = BertWordPieceTokenizer(
    clean_text=False,
    handle_chinese_chars=True,
    strip_accents=True,
    lowercase=True
)

# and train
tokenizer.train(files=fileList, vocab_size=29000, min_frequency=2,
                limit_alphabet=500, wordpieces_prefix='##',
                special_tokens=[
                    '[PAD]', '[UNK]', '[CLS]', '[SEP]', '[MASK]'])

tokenizer.save_model('./new_bert_vocab_2/', 'bert-wordpiece')

