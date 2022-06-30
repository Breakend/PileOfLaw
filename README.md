# PileOfLaw

This is the codebase used for the experiments and data scraping tools used for gathering Pile of law.

Note the Pile of Law dataset itself can be found here: https://huggingface.co/datasets/pile-of-law/pile-of-law

Pretrained models (though they may be undertrained) can be found here: 

https://huggingface.co/pile-of-law/legalbert-large-1.7M-1

https://huggingface.co/pile-of-law/legalbert-large-1.7M-2

Note, the main model we reference in the paper is *-2. 

We can make intermediate checkpoints every 50k steps available on request, we do not upload them all as it is a significant amount of data storage.

The EOIR privacy pretrained model is available at https://huggingface.co/pile-of-law/distilbert-base-uncased-finetuned-eoir_privacy

All model cards and datacards are included in the associated repositories. Code for the paper is available as follows.

## Dataset Creation

All of the tools used to scrape every subset of the data lives in the dataset_creation subfolder. 

## Privacy Experiments

The privacy experiments live under the privacy folder with a separate Readme explaining those sections.

## Toxicity Experiments

The toxicity experiments live under the toxicity subfolder

## Pretraining and fine-tuning

The pretraining processing scripts and fine-tuning scripts live under the pretraining folder.

## Data scrubbing

We also examine all datasets for SSNs. While we log all private info, we found that most APIs had a significant number of false positives. We narrowly looked for SSNs, but did not encounter any. It is possible the filters we use are not robust, but similarly all datasets we use should already be pre-filtered for such sensitive information also. Scripts for this can be found in the scrub folder.


## Citations

Please cite our work if you use any of the tools here and/or the data.

```
@article{hendersonkrass2022pileoflaw,
  title={Pile of Law: Learning Responsible Data Filtering from the Law and a 256GB Open-Source Legal Dataset},
  author={Henderson*, Peter and Krass*, Mark and Zheng, Lucia and Guha, Neel and Manning, Christopher and Jurafsky, Dan and Ho, Daniel E},
  year={2022}
}
```

Some of the datasets in this work are transformed from prior work. Please cite these works as well if you use this dataset:

```
@inproceedings{borchmann-etal-2020-contract,
    title = "Contract Discovery: Dataset and a Few-Shot Semantic Retrieval Challenge with Competitive Baselines",
    author = "Borchmann, {\L}ukasz  and
      Wisniewski, Dawid  and
      Gretkowski, Andrzej  and
      Kosmala, Izabela  and
      Jurkiewicz, Dawid  and
      Sza{\l}kiewicz, {\L}ukasz  and
      Pa{\l}ka, Gabriela  and
      Kaczmarek, Karol  and
      Kaliska, Agnieszka  and
      Grali{\'n}ski, Filip",
    booktitle = "Findings of the Association for Computational Linguistics: EMNLP 2020",
    month = nov,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.findings-emnlp.380",
    pages = "4254--4268",
    abstract = "We propose a new shared task of semantic retrieval from legal texts, in which a so-called contract discovery is to be performed {--} where legal clauses are extracted from documents, given a few examples of similar clauses from other legal acts. The task differs substantially from conventional NLI and shared tasks on legal information extraction (e.g., one has to identify text span instead of a single document, page, or paragraph). The specification of the proposed task is followed by an evaluation of multiple solutions within the unified framework proposed for this branch of methods. It is shown that state-of-the-art pretrained encoders fail to provide satisfactory results on the task proposed. In contrast, Language Model-based solutions perform better, especially when unsupervised fine-tuning is applied. Besides the ablation studies, we addressed questions regarding detection accuracy for relevant text fragments depending on the number of examples available. In addition to the dataset and reference results, LMs specialized in the legal domain were made publicly available.",
}

@data{T1/N1X6I4_2020,
    author = {Blair-Stanek, Andrew and Holzenberger, Nils and Van Durme, Benjamin},
    publisher = {Johns Hopkins University Data Archive},
    title = "{Tax Law NLP Resources}",
    year = {2020},
    version = {V2},
    doi = {10.7281/T1/N1X6I4},
    url = {https://doi.org/10.7281/T1/N1X6I4}
}

@article{hendrycks2021cuad,
    title={CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review}, 
    author={Dan Hendrycks and Collin Burns and Anya Chen and Spencer Ball},
    journal={arXiv preprint arXiv:2103.06268},
    year={2021}
}

@inproceedings{koehn2005europarl,
    title={Europarl: A parallel corpus for statistical machine translation},
    author={Koehn, Philipp and others},
    booktitle={MT summit},
    volume={5},
    pages={79--86},
    year={2005},
    organization={Citeseer}
}

@article{DBLP:journals/corr/abs-1805-01217,
    author    = {Marco Lippi and
    Przemyslaw Palka and
    Giuseppe Contissa and
    Francesca Lagioia and
    Hans{-}Wolfgang Micklitz and
    Giovanni Sartor and
    Paolo Torroni},
    title     = {{CLAUDETTE:} an Automated Detector of Potentially Unfair Clauses in
    Online Terms of Service},
    journal   = {CoRR},
    volume    = {abs/1805.01217},
    year      = {2018},
    url       = {http://arxiv.org/abs/1805.01217},
    archivePrefix = {arXiv},
    eprint    = {1805.01217},
    timestamp = {Mon, 13 Aug 2018 16:49:16 +0200},
    biburl    = {https://dblp.org/rec/bib/journals/corr/abs-1805-01217},
    bibsource = {dblp computer science bibliography, https://dblp.org}
}

@article{ruggeri2021detecting,
    title={Detecting and explaining unfairness in consumer contracts through memory networks},
    author={Ruggeri, Federico and Lagioia, Francesca and Lippi, Marco and Torroni, Paolo},
    journal={Artificial Intelligence and Law},
    pages={1--34},
    year={2021},
    publisher={Springer}
}

@inproceedings{10.1145/3462757.3466066,
    author = {Huang, Zihan and Low, Charles and Teng, Mengqiu and Zhang, Hongyi and Ho, Daniel E. and Krass, Mark S. and Grabmair, Matthias},
    title = {Context-Aware Legal Citation Recommendation Using Deep Learning},
    year = {2021},
    isbn = {9781450385268},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    url = {https://doi.org/10.1145/3462757.3466066},
    doi = {10.1145/3462757.3466066},
    abstract = {Lawyers and judges spend a large amount of time researching the proper legal authority
    to cite while drafting decisions. In this paper, we develop a citation recommendation
    tool that can help improve efficiency in the process of opinion drafting. We train
    four types of machine learning models, including a citation-list based method (collaborative
    filtering) and three context-based methods (text similarity, BiLSTM and RoBERTa classifiers).
    Our experiments show that leveraging local textual context improves recommendation,
    and that deep neural models achieve decent performance. We show that non-deep text-based
    methods benefit from access to structured case metadata, but deep models only benefit
    from such access when predicting from context of insufficient length. We also find
    that, even after extensive training, RoBERTa does not outperform a recurrent neural
    model, despite its benefits of pretraining. Our behavior analysis of the RoBERTa model
    further shows that predictive performance is stable across time and citation classes.},
    booktitle = {Proceedings of the Eighteenth International Conference on Artificial Intelligence and Law},
    pages = {79–88},
    numpages = {10},
    keywords = {neural natural language processing, legal opinion drafting, citation recommendation, legal text, citation normalization},
    location = {S\~{a}o Paulo, Brazil},
    series = {ICAIL '21}
}
```
