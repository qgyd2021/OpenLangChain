#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os
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


def get_args():
    parser = argparse.ArgumentParser()

    # https://arxiv.org/abs/2203.02155
    parser.add_argument(
        "--arxiv_id",
        default="2203.02155",
        type=str
    )
    parser.add_argument(
        "--save_dir",
        default=(project_path / "cache/arxiv_pdf").as_posix(),
        type=str
    )
    parser.add_argument(
        "--query",
        default="what is instruction GPT ?",
        type=str
    )

    parser.add_argument("--separator", default=". ", type=str)

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

    args = parser.parse_args()
    return args


def main():
    args = get_args()

    # filename
    os.makedirs(args.save_dir, exist_ok=True)
    filename = "{}/{}.pdf".format(args.save_dir, args.arxiv_id)

    # download documents
    if not os.path.exists(filename):
        url = "https://arxiv.org/pdf/{}.pdf".format(args.arxiv_id)
        resp = requests.get(url)
        with open(filename, "wb") as f:
            f.write(resp.content)

    # load documents
    loader = PyPDFLoader(filename)
    documents: Iterator[Document] = loader.load()

    # document to chunks
    text_splitter = CharacterTextSplitter(separator=". ", chunk_size=500, chunk_overlap=150)
    documents: List[Document] = text_splitter.split_documents(documents)
    print("chunks count: {}".format(len(documents)))

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

    # chunks to vector
    vector_db: Chroma = Chroma.from_documents(
        documents,
        embedding=hf_embedding,
        persist_directory=args.persist_directory
    )
    vector_db.persist()

    # search
    documents: List[Document] = vector_db.similarity_search(
        query=args.query,
        k=4,
    )

    for document in documents:
        print(document.page_content)
        print("-" * 200)

    return


if __name__ == '__main__':
    main()
