
# EOIR Pseudonyms Experiment

In this experiment we first create a dataset of paragraphs from:

```
python create_pseodonyms_dataset.py
``` 

We upload the generated dataset linking data to labels in [this HuggingFace Repo](https://huggingface.co/datasets/pile-of-law/eoir_privacy).

Then we use a Colab notebook to train a distillbert model, also available as an ipython notebook:

```
EOIR.ipynb
```

The resulting model is a runable model which we [also upload to HF](https://huggingface.co/pile-of-law/distilbert-base-uncased-finetuned-eoir_privacy).

Then we run a perturbation experiment via the script as seen in

```
EOIR_validation_exp.ipynb 
```

For the causal lexicon experiment we use:

```
causal_exp.py
```

