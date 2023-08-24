#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
from typing import List

from langchain.embeddings.huggingface import HuggingFaceEmbeddings

from project_settings import project_path


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name",
        default="sentence-transformers/all-mpnet-base-v2",
        type=str
    )
    parser.add_argument(
        "--pretrained_models_dir",
        default=(project_path / "pretrained_models").as_posix(),
        type=str
    )
    parser.add_argument("--device", default="cpu", type=str)
    parser.add_argument("--normalize_embeddings", action="store_true")

    parser.add_argument("--query", default="what the date today ?", type=str)

    args = parser.parse_args()
    return args


def main():
    args = get_args()

    hf = HuggingFaceEmbeddings(
        model_name=args.model_name,
        cache_folder=args.pretrained_models_dir,
        model_kwargs={
            "device": args.device,
        },
        encode_kwargs={
            "normalize_embeddings": args.normalize_embeddings
        },
    )

    result: List[float] = hf.embed_query(text=args.query)
    print(len(result))

    result: List[List[float]] = hf.embed_documents(texts=[args.query])
    print(len(result))
    return


if __name__ == '__main__':
    main()
