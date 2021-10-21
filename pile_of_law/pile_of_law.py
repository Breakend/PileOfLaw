# coding=utf-8
# Copyright 2021 The HuggingFace Datasets Authors and the current dataset script contributor.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Pile of Law Corpus"""


import os
import re
from itertools import chain
import json
try:
    import lzma as xz
except ImportError:
    import pylzma as xz

from .download_mapping import DOWNLOAD_MAPPING
import datasets


_CITATION = """\
@misc{todo,
  title={The Pile of Law Corpus},
  author={todo},
  howpublished{\\url{todo}},
  year={2021}
}
"""

_DESCRIPTION = """\
A dataset for pretraining legal models
"""

_URL = "TODO"

class PileOfLaw(datasets.GeneratorBasedBuilder):
    """The Open WebText dataset."""

    BUILDER_CONFIGS = [
        datasets.BuilderConfig(
            name="plain_text",
            description="Plain text",
            version=datasets.Version("1.0.0"),
        )
    ]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features({"text": datasets.Value("string"), "url" : datasets.Value("string")}),
            homepage="TODO",
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        val_urls = []
        train_urls = []
        for name, info in DOWNLOAD_MAPPING.items():
            val_urls.append(info["urls"]["validation"])
            train_urls.append(info["urls"]["train"])
        train_downloaded_files = dl_manager.download(train_urls)
        validation_downloaded_files = dl_manager.download(val_urls)
        return [
            datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={"filepaths": train_downloaded_files}),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION, gen_kwargs={"filepaths": validation_downloaded_files}
            ),
        ]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "text": datasets.Value("string"),
                    "timestamp": datasets.Value("string"),
                    "url": datasets.Value("string"),
                }
            ),
            supervised_keys=None,
            homepage=_URL,
            citation=_CITATION,
        )

    def _generate_examples(self, filepaths):
        """This function returns the examples in the raw (text) form by iterating on all the files."""
        id_ = 0
        for filepath in filepaths:
            logger.info("generating examples from = %s", filepath)
            with lzma.open(filepath) as f:
                for line in f:
                    if line:
                        example = json.loads(str(line, 'utf-8'))
                        yield id_, example
                        id_ += 1
