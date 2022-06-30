
# Vocab

We use new_vocab.py for generating part of the vocabulary and the rest is supplemented via a random sampling of Black's law dictionary.

# Chunkification and Randomization

We use the chunkify_and_hd5.py file to segment and shuffle the data into shards. Note that each shard consists of a homogeneous sampling across data segments. We find that not doing this created extremely large instabilities.

# Fine-tuning

Fine-tuning code is in pol-finetuning-main