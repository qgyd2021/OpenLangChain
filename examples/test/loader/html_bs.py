#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import json
from typing import List

from langchain.schema import Document
from langchain.document_loaders.html_bs import BSHTMLLoader
import requests


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", default="bs_html.html", type=str)
    # parser.add_argument("--html_url", default=None, type=str)
    parser.add_argument("--html_url", default="https://www.zhihu.com/question/320763265/answer/2360423247", type=str)

    parser.add_argument("--open_encoding", default="utf-8", type=str)
    parser.add_argument("--bs_kwargs", default="{\"features\": \"html.parser\"}", type=str)
    parser.add_argument("--get_text_separator", default="", type=str)

    args = parser.parse_args()
    return args


def main():
    args = get_args()

    if args.html_url is not None:
        resp = requests.get(args.html_url)
        html_doc = resp.content.decode(args.open_encoding)

        with open(args.file_path, "w", encoding=args.open_encoding) as f:
            f.write(html_doc)

    bs_kwargs = json.loads(args.bs_kwargs)
    loader = BSHTMLLoader(
        file_path=args.file_path,
        open_encoding=args.open_encoding,
        bs_kwargs=bs_kwargs,
        get_text_separator=args.get_text_separator,
    )

    documents: List[Document] = loader.load()
    document = documents[0]
    print(document.page_content)
    print(type(document.page_content))
    print(len(document.page_content))
    print(document.metadata)

    return


if __name__ == '__main__':
    main()
