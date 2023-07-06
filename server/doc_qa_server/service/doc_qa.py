#!/usr/bin/python3
# -*- coding: utf-8 -*-
from abc import abstractmethod
import logging
import os
import shutil
from typing import Iterator, List

from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI, HumanInputLLM, HuggingFaceHub
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma, VectorStore

from server.doc_qa_server import settings

logger = logging.getLogger('server')


class DocQA(object):
    def __call__(self, *args, **kwargs):
        return self.search(*args, **kwargs)

    @abstractmethod
    def search(self, filename: str, query: str, **kwargs):
        raise NotImplementedError


class PdfOpenAIOpenAIDocQA(DocQA):
    def __init__(self,
                 openai_api_key: str,
                 persist_directory: str
                 ):
        super(PdfOpenAIOpenAIDocQA, self).__init__()
        self.openai_api_key = openai_api_key
        self.persist_directory = persist_directory

        #
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key
        )
        self.llm = OpenAI(
            openai_api_key=self.openai_api_key
        )

    def load_file(self, filename: str, chunk_size: int, chunk_overlap: int) -> List[Document]:
        loader = PyPDFLoader(filename)
        documents: Iterator[Document] = loader.load()

        # document to chunks
        text_splitter = CharacterTextSplitter(separator="", chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        documents: List[Document] = text_splitter.split_documents(documents)

        return documents

    def build_vector_db(self, documents: List[Document]):
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
        os.makedirs(self.persist_directory, exist_ok=False)

        vector_db: Chroma = Chroma.from_documents(
            documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        vector_db.persist()
        return vector_db

    def search(self, filename: str, query: str, **kwargs):
        top_k = kwargs.get('top_k', 3)
        chunk_size = kwargs.get('chunk_size', 100)
        chunk_overlap = kwargs.get('chunk_overlap', 20)

        documents = self.load_file(filename, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        vector_db = self.build_vector_db(documents)

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=vector_db.as_retriever(search_kwargs={'k': top_k}),
            return_source_documents=True
        )

        result = qa_chain({'query': query})
        return result


class PdfHfOpenAIDocQA(DocQA):
    def __init__(self,
                 hf_embedding_repo_id: str,
                 pretrained_models_directory: str,
                 normalize_embeddings: str,
                 device: str,
                 openai_api_key: str,
                 persist_directory: str
                 ):
        super(PdfHfOpenAIDocQA, self).__init__()
        self.hf_embedding_repo_id = hf_embedding_repo_id
        self.pretrained_models_directory = pretrained_models_directory
        self.device = device
        self.normalize_embeddings = normalize_embeddings

        self.openai_api_key = openai_api_key
        self.persist_directory = persist_directory

        #
        self.hf_embedding = HuggingFaceEmbeddings(
            model_name=self.hf_embedding_repo_id,
            cache_folder=self.pretrained_models_directory,
            model_kwargs={
                "device": self.device,
            },
            encode_kwargs={
                "normalize_embeddings": self.normalize_embeddings
            },
        )
        self.llm = OpenAI(
            openai_api_key=self.openai_api_key
        )

    def load_file(self, filename: str) -> List[Document]:
        loader = PyPDFLoader(filename)
        documents: Iterator[Document] = loader.load()

        # document to chunks
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=150)
        documents: List[Document] = text_splitter.split_documents(documents)

        return documents

    def build_vector_db(self, persist_directory: str, documents: List[Document]):
        vector_db: Chroma = Chroma.from_documents(
            documents,
            embedding=self.hf_embedding,
            persist_directory=persist_directory
        )
        if not os.path.exists(persist_directory):
            vector_db.persist()
        return vector_db

    def search(self, filename: str, query: str, **kwargs):
        top_k = kwargs.get('top_k', 3)

        documents = self.load_file(filename)

        _, fn = os.path.split(filename)
        persist_directory = os.path.join(self.persist_directory, fn)
        vector_db = self.build_vector_db(persist_directory, documents)

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=vector_db.as_retriever(search_kwargs={'k': top_k}),
            return_source_documents=True
        )

        result = qa_chain({'query': query})
        return result


class PdfHfHumanInputLLMDocQA(DocQA):
    def __init__(self,
                 hf_embedding_repo_id: str,
                 pretrained_models_directory: str,
                 normalize_embeddings: str,
                 device: str,
                 persist_directory: str
                 ):
        super(PdfHfHumanInputLLMDocQA, self).__init__()
        self.hf_embedding_repo_id = hf_embedding_repo_id
        self.pretrained_models_directory = pretrained_models_directory
        self.device = device
        self.normalize_embeddings = normalize_embeddings

        self.persist_directory = persist_directory

        #
        self.hf_embedding = HuggingFaceEmbeddings(
            model_name=self.hf_embedding_repo_id,
            cache_folder=self.pretrained_models_directory,
            model_kwargs={
                "device": self.device,
            },
            encode_kwargs={
                "normalize_embeddings": self.normalize_embeddings
            },
        )
        self.llm = HumanInputLLM()

    def load_file(self, filename: str) -> List[Document]:
        loader = PyPDFLoader(filename)
        documents: Iterator[Document] = loader.load()

        # document to chunks
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=150)
        documents: List[Document] = text_splitter.split_documents(documents)

        return documents

    def build_vector_db(self, persist_directory: str, documents: List[Document]):
        vector_db: Chroma = Chroma.from_documents(
            documents,
            embedding=self.hf_embedding,
            persist_directory=persist_directory
        )
        if not os.path.exists(persist_directory):
            vector_db.persist()
        return vector_db

    def search(self, filename: str, query: str, **kwargs):
        top_k = kwargs.get('top_k', 3)

        documents = self.load_file(filename)

        _, fn = os.path.split(filename)
        persist_directory = os.path.join(self.persist_directory, fn)
        vector_db = self.build_vector_db(persist_directory, documents)

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=vector_db.as_retriever(search_kwargs={'k': top_k}),
            return_source_documents=True
        )

        result = qa_chain({'query': query})
        return result


class PdfHfHfDocQA(DocQA):
    def __init__(self,
                 hf_embedding_repo_id: str,
                 hf_llm_repo_id: str,
                 pretrained_models_directory: str,
                 normalize_embeddings: str,
                 device: str,
                 hf_api_token: str,
                 persist_directory: str
                 ):
        super(PdfHfHfDocQA, self).__init__()
        self.hf_embedding_repo_id = hf_embedding_repo_id
        self.hf_llm_repo_id = hf_llm_repo_id
        self.pretrained_models_directory = pretrained_models_directory
        self.device = device
        self.normalize_embeddings = normalize_embeddings

        self.hf_api_token = hf_api_token
        self.persist_directory = persist_directory

        #
        self.hf_embedding = HuggingFaceEmbeddings(
            model_name=self.hf_embedding_repo_id,
            cache_folder=self.pretrained_models_directory,
            model_kwargs={
                "device": self.device,
            },
            encode_kwargs={
                "normalize_embeddings": self.normalize_embeddings
            },
        )
        self.llm = HuggingFaceHub(
            repo_id=self.hf_llm_repo_id,
            huggingfacehub_api_token=self.hf_api_token,
        )

    def load_file(self, filename: str) -> List[Document]:
        loader = PyPDFLoader(filename)
        documents: Iterator[Document] = loader.load()

        # document to chunks
        text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        documents: List[Document] = text_splitter.split_documents(documents)

        return documents

    def build_vector_db(self, persist_directory: str, documents: List[Document]):
        vector_db: Chroma = Chroma.from_documents(
            documents,
            embedding=self.hf_embedding,
            persist_directory=persist_directory
        )
        if not os.path.exists(persist_directory):
            vector_db.persist()
        return vector_db

    def search(self, filename: str, query: str, **kwargs):
        top_k = kwargs.get('top_k', 3)

        documents = self.load_file(filename)

        _, fn = os.path.split(filename)
        persist_directory = os.path.join(self.persist_directory, fn)
        vector_db = self.build_vector_db(persist_directory, documents)

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=vector_db.as_retriever(search_kwargs={'k': top_k}),
            return_source_documents=True
        )

        result = qa_chain({'query': query})
        return result


engine_to_chain = {
    'pdf_openai_openai': PdfOpenAIOpenAIDocQA(
        openai_api_key=settings.openai_api_key,
        persist_directory=os.path.join(settings.temp_directory, 'persist_directory/pdf_openai_openai'),
    ),
    'pdf_hf_openai': PdfHfOpenAIDocQA(
        hf_embedding_repo_id=settings.hf_embedding_repo_id,
        pretrained_models_directory=settings.pretrained_models_directory,
        normalize_embeddings=False,
        device='cpu',
        openai_api_key=settings.openai_api_key,
        persist_directory=os.path.join(settings.temp_directory, 'persist_directory/pdf_hf_openai'),
    ),
    'pdf_hf_human': PdfHfHumanInputLLMDocQA(
        hf_embedding_repo_id=settings.hf_embedding_repo_id,
        pretrained_models_directory=settings.pretrained_models_directory,
        normalize_embeddings=False,
        device='cpu',
        persist_directory=os.path.join(settings.temp_directory, 'persist_directory/pdf_hf_human'),
    ),
    'pdf_hf_hf': PdfHfHfDocQA(
        hf_embedding_repo_id=settings.hf_embedding_repo_id,
        hf_llm_repo_id=settings.hf_llm_repo_id,
        pretrained_models_directory=settings.pretrained_models_directory,
        normalize_embeddings=False,
        device='cpu',
        hf_api_token=settings.hf_api_token,
        persist_directory=os.path.join(settings.temp_directory, 'persist_directory/pdf_hf_hf'),
    )
}


if __name__ == '__main__':
    pass
