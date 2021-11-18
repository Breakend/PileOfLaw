# This script downloads the raw data files from the Google drive
import sys
sys.path.append("..")
import gdown
import os
from pile_of_law.download_mapping import DOWNLOAD_MAPPING


def main():
    output_directory = "raw_data/"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    failed = []
    for dataset in DOWNLOAD_MAPPING:
        for split in DOWNLOAD_MAPPING[dataset]['urls']:
            url = DOWNLOAD_MAPPING[dataset]['urls'][split]
            id = url.replace("https://drive.google.com/file/d/", "")
            id = id.replace("/view?usp=sharing", "")
            download_link = f"https://drive.google.com/u/1/uc?id={id}&export=download"
            filename = gdown.download(download_link, output=output_directory)
            if filename is None:
                failed.append(download_link)
    print(f"Download failed for the following files: {failed}")


if __name__ == '__main__':
    main()