#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
from typing import List

from langchain.chains.combine_documents.stuff import StuffDocumentsChain, _get_default_document_prompt
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering.stuff_prompt import CHAT_PROMPT
from langchain.llms.huggingface_hub import HuggingFaceHub
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import Document

import project_settings as settings


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hf_api_token",
        default=settings.environment.get("hf_api_token", default=None, dtype=str),
        type=str
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    llm = HuggingFaceHub(
        repo_id="gpt2",
        # repo_id="anon8231489123/gpt4-x-alpaca-13b-native-4bit-128g",
        huggingfacehub_api_token=args.hf_api_token,
    )
    llm_chain = LLMChain(llm=llm, prompt=CHAT_PROMPT)

    document_prompt: PromptTemplate = _get_default_document_prompt()
    document_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_prompt=document_prompt,
        document_variable_name='context',
        document_separator=""
    )

    documents: List[Document] = [
        Document(page_content="document1"),
        Document(page_content="document2"),
    ]

    question = "what is it ?"
    completions, _ = document_chain.combine_docs(docs=documents, question=question)
    print(completions)
    print(type(completions))
    print(len(completions))

    document_chain.__call__()
    return


if __name__ == '__main__':
    main()
