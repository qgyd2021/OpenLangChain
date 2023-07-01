#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import project_settings as settings


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--openai_api_key",
        default=settings.environment.get("openai_api_key", default=None, dtype=str),
        type=str
    )
    args = parser.parse_args()
    return args


def demo1():
    args = get_args()

    # llm
    llm = OpenAI(
        temperature=0.9,
        openai_api_key=args.openai_api_key
    )
    result: str = llm.predict("What would be a good company name for a company that makes colorful socks?")
    print(result)
    return


def demo2():
    # prompt
    prompt = PromptTemplate.from_template("What is a good name for a company that makes {product}?")
    result: str = prompt.format(product="colorful socks")
    print(result)
    return


def demo3():
    args = get_args()

    # llm
    llm = OpenAI(
        temperature=0.9,
        openai_api_key=args.openai_api_key
    )

    # prompt
    prompt: PromptTemplate = PromptTemplate.from_template("What is a good name for a company that makes {product}?")

    # llm chain
    chain = LLMChain(llm=llm, prompt=prompt)
    result: str = chain.run("colorful socks")
    print(result)
    return


if __name__ == '__main__':
    demo1()
