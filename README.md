# PileOfLaw

## Instructions for adding data

1. Scrape the relevant dataset such that a logically grouped set of documents is in a jsonlines file (ending in .jsonl), these should then be compressed with xz. Make sure that for each source there is a 75/25 split for train and validation and specify those in the download_mapping.py file. For datasets that are centrally located elsewhere or behind separate API key, you can just specify a download from that location and update the pile_of_law.py with a special subroutine to download that. Add scraping code to the dataset_creation/<datasource_name> folder. If a series of documents should be logically stringed together such that a longformer-type model might be able to make cross-document connections, please go ahaead and add those as a single json line (i.e., a legal brief might go first with the answer brief after and the opinion added after that). Please do your best to de-duplicate as much as possible. 
2. You can add the scraped and compressed data to the Google Drive (ask for access if you don't have it yet). In the future the storage location may change.
3. Add a download link to the download_mapping file, specifying train and validation splits.

