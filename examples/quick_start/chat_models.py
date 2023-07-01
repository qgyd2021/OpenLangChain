#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
from typing import List

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

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

    # chat model
    chat = ChatOpenAI(
        temperature=0,
        openai_api_key=args.openai_api_key
    )
    result: AIMessage = chat.predict_messages(messages=[
        HumanMessage(content="Translate this sentence from English to French. I love programming.")
    ])
    print(result)
    result: str = chat.predict("Translate this sentence from English to French. I love programming.")
    print(result)
    return


def demo2():
    # template
    template = "You are a helpful assistant that translates {input_language} to {output_language}."
    system_message_prompt = SystemMessagePromptTemplate.from_template(template=template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    result: List[BaseMessage] = chat_prompt.format_messages(input_language="English", output_language="French", text="I love programming.")
    print(result[0].content)
    print(result[1].content)
    return


def demo3():
    args = get_args()

    # chat model
    chat = ChatOpenAI(
        temperature=0,
        openai_api_key=args.openai_api_key
    )

    # template
    template = "You are a helpful assistant that translates {input_language} to {output_language}."
    system_message_prompt = SystemMessagePromptTemplate.from_template(template=template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    # chain
    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result: str = chain.run(input_language="English", output_language="French", text="I love programming.")
    print(result)
    return


if __name__ == '__main__':
    demo3()
