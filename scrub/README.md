## Scrub
This directory contains the script, `scrub.py`, for scrubbing the dataset for sensitive information. `scrub.py` writes the scrubbed data to jsonl.xz files in the `data_scrubbed` directory and the filth data to json files in the `filth` directory.

The filth data json files contain File Filth JSON objects with the following structure:
```
{
	filename: name of the data file (dtype: string)
	filth_count: total count of filth detected across all documents in the data file (dtype: integer)
	word_count: total count of all words across all documents in the data file (dtype: integer)
	filth_doc_count: total count of documents with >0 filth in the data file (dtype: integer)
	doc_count: total count of documents in the data file (dtype: integer)
	filth_data: list of Document Filth JSON objects, corresponding to each document in the data file, order of Document Filth JSON objects perserves document order from original data file (dtype: list[Document Filth JSON object])
}
```

where a Document Filth JSON object has the following structure:
```
{
	url: source url where document was scraped (dtype: string)
	filth_count: count of filth detected in document (dtype: integer)
	word_count: count of all words in document (dtype: integer)
	filth: list of Filth JSON objects, corresponding to each item of filth detected in the document (dtype: list[Filth JSON object])
}
```

and a Filth JSON object has the following structure:
```
{
	type: type of filth, corresponds to type field in [scrubadub.filth.Filth](https://scrubadub.readthedocs.io/en/stable/api_scrubadub_filth.html) class (dtype: string or list[string])
	text: filth text / what was scrubbed out, corresponds to text field in [scrubadub.filth.Filth](https://scrubadub.readthedocs.io/en/stable/api_scrubadub_filth.html) class (dtype: string or list[string])
	merged: if is MergedFilth, filth is merged when multiple types of filth are detected for overlapping text, if merged = true, type and text will be lists (that share the same order) of all of the types and corresponding texts for which filth was detected (dtype: boolean)
}
```