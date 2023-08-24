#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse

from langchain.text_splitter import TokenTextSplitter
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.few_shot_with_templates import FewShotPromptWithTemplates


def get_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument("--separator", default="\n", type=str)
    parser.add_argument("--separator", default="", type=str)

    parser.add_argument("--chunk_size", default=100, type=int)
    parser.add_argument("--chunk_overlap", default=20, type=int)
    parser.add_argument("--keep_separator", action="store_true")
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    prompt: FewShotPromptTemplate = FewShotPromptTemplate(

    )

    return


if __name__ == '__main__':
    main()
