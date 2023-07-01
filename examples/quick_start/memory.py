#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse

from langchain import OpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

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

    # memory llm
    llm = OpenAI(
        temperature=0,
        openai_api_key=args.openai_api_key
    )
    conversation = ConversationChain(llm=llm, verbose=True)

    answer: str = conversation.run("Hi there!")
    print(answer)

    answer: str = conversation.run("I'm doing well! Just having a conversation with an AI.")
    print(answer)

    return


def demo2():
    args = get_args()

    # memory chat models
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "The following is a friendly conversation between a human and an AI. The AI is talkative and "
            "provides lots of specific details from its context. If the AI does not know the answer to a "
            "question, it truthfully says it does not know."
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=args.openai_api_key
    )
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm, verbose=True)

    answer: str = conversation.predict(input="Hi there!")
    print(answer)

    answer: str = conversation.predict(input="I'm doing well! Just having a conversation with an AI.")
    print(answer)

    answer: str = conversation.predict(input="Tell me about yourself.")
    print(answer)

    return


if __name__ == '__main__':
    # demo1()
    demo2()
