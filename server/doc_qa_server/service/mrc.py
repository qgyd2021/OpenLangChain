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
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.question_answering.stuff_prompt import PROMPT

from server.doc_qa_server import settings

logger = logging.getLogger('server')


class DocQA(object):
    def __call__(self, *args, **kwargs):
        return self.search(*args, **kwargs)

    @abstractmethod
    def search(self, documents: str, query: str, **kwargs) -> str:
        raise NotImplementedError


class OpenAIDocQA(DocQA):
    def __init__(self,
                 openai_api_key: str,
                 ):
        super(OpenAIDocQA, self).__init__()
        self.openai_api_key = openai_api_key

        self.llm = OpenAI(
            openai_api_key=self.openai_api_key
        )

        self.prompt: PromptTemplate = PROMPT

        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def search(self, documents: str, query: str, **kwargs) -> str:
        outputs: str = self.llm_chain.predict(question=query, context=documents)
        return outputs


engine_to_chain = {
    'openai': OpenAIDocQA(
        openai_api_key=settings.openai_api_key,
    ),
}


if __name__ == '__main__':
    pass
