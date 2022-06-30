
# Processing Supreme Court Opinions with Toxicity APIs

The scotus_only* files run toxicity scores over only scotus documents. Note: for this we use the case law access project supreme court decisions data because it contains accurate metadata for opinion dates. To run this, you will need to also download the bulk scotus opinions from CAP. The output of these scripts, a sentence by sentence scoring of all Supreme Court opinions can be found here:

https://drive.google.com/drive/folders/1QvLdlBGHZYX6mv5HCh1SL_QZLCs5yN6-?usp=sharing

This is roughly 11Gb of data. 

The data is formatted such that each row is a sentence indexed by document and a score from a different API. The mapping from sentence and document indices can be found in sent_mapping.pkl

# Figure 2

The Figure 2 generation code can be found in fig2

