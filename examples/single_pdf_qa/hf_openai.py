#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
https://betterprogramming.pub/d1864d47e339

"""
import argparse
from typing import Iterator, List

from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.llms import OpenAI
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma, VectorStore

from project_settings import project_path
import project_settings as settings


def get_args():
    parser = argparse.ArgumentParser()

    # https://arxiv.org/abs/2203.02155
    parser.add_argument(
        "--filename",
        default=(project_path / "examples/single_pdf_qa/data_dir/2203.02155.pdf").as_posix(),
        type=str
    )
    parser.add_argument(
        "--query",
        default="what is instruction GPT ?",
        type=str
    )

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
        "--cache_folder",
        default=(project_path / "cache_folder").as_posix(),
        type=str
    )
    parser.add_argument("--device", default="cpu", type=str)
    parser.add_argument("--normalize_embeddings", action="store_true")

    # secret key
    parser.add_argument(
        "--openai_api_key",
        default=settings.environment.get("openai_api_key", default=None, dtype=str),
        type=str
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    # load documents
    loader = PyPDFLoader(args.filename)
    documents: Iterator[Document] = loader.load()

    # document to chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=150)
    documents: List[Document] = text_splitter.split_documents(documents)

    # embedding
    hf_embedding = HuggingFaceEmbeddings(
        model_name=args.model_name,
        cache_folder=args.cache_folder,
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

    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(
            openai_api_key=args.openai_api_key
        ),
        retriever=vector_db.as_retriever(search_kwargs={'k': 3}),
        return_source_documents=True
    )

    result = qa_chain({'query': args.query})

    print("query: {}".format(args.query))
    print("result: {}".format(result['result']))
    print("source_documents: {}".format(result['source_documents']))

    # Instruction GPT is a type of language model that is designed to
    # be used in customer assistant applications. It is optimized to
    # be better at following explicit constraints in the instruction
    # and attempting the correct instruction, and less likely to 'hallucinate'.
    # It has been compared to other language models such as FLAN and T0,
    # and is found to be more appropriate in the context of a customer assistant.
    return


if __name__ == '__main__':
    main()
