#!/usr/bin/python3
# -*- coding: utf-8 -*-
from typing import List

from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

openai_api_key = "${openai_api_key}"

text = """
Making language models bigger does not inherently make them better at following
a user’s intent. For example, large language models can generate outputs that
are untruthful, toxic, or simply not helpful to the user. In other words, these
models are not aligned with their users. In this paper, we show an avenue for
aligning language models with user intent on a wide range of tasks by ﬁne-tuning
with human feedback.
"""

separator = "\n"

splitter = CharacterTextSplitter(
    separator=separator,
    chunk_size=100,
    chunk_overlap=20,
    add_start_index=False
)

document = Document(
    page_content=text,
    metadata={
        'source': 'filename',
        'page': 0
    }
)

# document to chunks
documents: List[Document] = splitter.split_documents(documents=[document])

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
vector_db = Chroma.from_documents(
    documents,
    embedding=OpenAIEmbeddings(
        openai_api_key=openai_api_key
    ),
    persist_directory='./data'
)

vector_db.search("what is language models. ")
