#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os
import shutil
from typing import Iterator, List

from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.llms import OpenAI
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma, VectorStore
import requests

from project_settings import project_path
import project_settings as settings


DEFAULT_TEXT = """
Making language models bigger does not inherently make them better at following
a user’s intent. For example, large language models can generate outputs that
are untruthful, toxic, or simply not helpful to the user. In other words, these
models are not aligned with their users. In this paper, we show an avenue for
aligning language models with user intent on a wide range of tasks by ﬁne-tuning
with human feedback.
"""


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--text", default=DEFAULT_TEXT, type=str)
    parser.add_argument("--separator", default="", type=str)
    parser.add_argument("--chunk_size", default=100, type=int)
    parser.add_argument("--chunk_overlap", default=20, type=int)

    # chroma
    parser.add_argument(
        "--persist_directory",
        default=(project_path / "cache/chroma/persist_directory").as_posix(),
        type=str
    )

    # hugging face embedding
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

    # query
    parser.add_argument("--query", default="what is instruction GPT ?", type=str)
    parser.add_argument("--search_type", default="similarity", type=str)

    args = parser.parse_args()
    return args


def main():
    args = get_args()

    splitter = CharacterTextSplitter(
        separator=args.separator,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        add_start_index=False
    )

    document = Document(
        page_content=args.text,
        metadata={
            'source': 'filename',
            'page': 0,
            'category': 'arxiv'
        }
    )

    # document to chunks
    documents: List[Document] = splitter.split_documents(documents=[document])
    print("documents count: {}".format(len(documents)))

    # embedding
    hf_embedding = HuggingFaceEmbeddings(
        model_name=args.model_name,
        cache_folder=args.pretrained_models_dir,
        model_kwargs={
            "device": args.device,
        },
        encode_kwargs={
            "normalize_embeddings": args.normalize_embeddings
        },
    )

    if os.path.exists(args.persist_directory):
        shutil.rmtree(args.persist_directory)
    os.makedirs(args.persist_directory)

    # chunks to vector
    vector_db = Chroma.from_documents(
        documents,
        embedding=hf_embedding,
        persist_directory=args.persist_directory
    )
    vector_db.search()

    outputs = vector_db.similarity_search(query=args.query, k=4, filter={"category": "arxiv"})
    print(outputs)

    outputs = vector_db.similarity_search(query=args.query, k=4, filter={"category": "chroma"})
    print(outputs)

    return


if __name__ == '__main__':
    main()
