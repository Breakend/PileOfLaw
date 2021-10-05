# PileOfLaw

## Instructions for adding data

1. Scrape the relevant dataset such that a logically grouped set of documents is in a jsonlines file (ending in .jsonl), these should then be compressed with xz. Make sure that for each source there is a 75/25 split for train and validation and specify those in the download_mapping.py file. Each line should have {"text" : (text), "url" : (where you got it from), "created_timestamp" : when_the_document_was_created, "downloaded_timestamp" : datetime.date.today().strftime("%m-%d-%Y"),} and any other metadata you think might be interesting to include.
2. For datasets that are centrally located elsewhere or behind separate API key, you can just specify a download from that location and update the pile_of_law.py with a special subroutine to download and process that. Alternatively, we might rehost the dataset elsewhere and just verify permissions somehow?
3. Add your scraping/processing code to the dataset_creation/<datasource_name> folder. If a series of documents should be logically stringed together such that a longformer-type model might be able to make cross-document connections, please go ahaead and add those as a single json line (i.e., a legal brief might go first with the answer brief after and the opinion added after that). Please do your best to de-duplicate as much as possible. 
4. You can add the scraped and compressed data to the Google Drive (ask for access if you don't have it yet). In the future the storage location may change.
5. Add a download link to the download_mapping file, specifying train and validation splits.
6. If a license is involved, make sure it is not super restrictive. We will have a DMCA process, but still better to avoid takedown requests.

## Other papers to cite

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
