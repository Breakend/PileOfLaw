# pol-finetuning

## Setup
- Create `pol_models` directory
    - Download Model4 (Models4 folder in GDrive) and pol-roberta weights from the Google Drive to the following paths in `pol_models`
       ```
       pol_models
            Model4
                config.json
                pytorch_model.bin
                tokenizer_config.json
                vocab.txt
       ```
- Conda env file: `environment.yml`
- Originally run on GCP instance with 
4 x NVIDIA Tesla A100, adjust batch size according to the machine you're running on


