#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse

from langchain.chains.llm import LLMChain
from langchain.llms.huggingface_hub import HuggingFaceHub
from langchain.chains.question_answering.stuff_prompt import CHAT_PROMPT

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

    print(CHAT_PROMPT.input_variables)

    outputs = llm_chain.predict(question='how are you ?', context='your are fine.')
    print(outputs)
    print(type(outputs))
    print(len(outputs))
    return


if __name__ == '__main__':
    main()
