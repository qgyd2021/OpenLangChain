#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import List

from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma


# chunks to vector
vector_db = Chroma(
    embedding_function=OpenAIEmbeddings(
        openai_api_key="openai_api_key"
    ),
    persist_directory='./data'
)

collection = vector_db.get(include=["embeddings"])
print(collection.keys())
print(collection)


if __name__ == '__main__':
    pass
