#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse

from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

import project_settings as settings


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--openai_api_key",
        default=settings.environment.get("openai_api_key", default=None, dtype=str),
        type=str
    )
    parser.add_argument(
        "--serpapi_api_key",
        default=settings.environment.get("serpapi_api_key", default=None, dtype=str),
        type=str
    )
    args = parser.parse_args()
    return args


def demo1():
    args = get_args()

    # agent llm
    llm = OpenAI(
        temperature=0.9,
        openai_api_key=args.openai_api_key
    )

    # The tools we'll give the Agent access to. Note that the 'llm-math' tool uses an LLM, so we need to pass that in.
    tools = load_tools(
        tool_names=["serpapi", "llm-math"],
        serpapi_api_key=args.serpapi_api_key,
        llm=llm
    )

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    result: str = agent.run("What was the high temperature in SF yesterday in Fahrenheit? What is that number raised to the .023 power?")
    print(result)

    return


def demo2():
    args = get_args()

    # agent chat models
    chat = ChatOpenAI(
        temperature=0.9,
        openai_api_key=args.openai_api_key
    )

    # The tools we'll give the Agent access to. Note that the 'llm-math' tool uses an LLM, so we need to pass that in.
    llm = OpenAI(
        temperature=0,
        openai_api_key=args.openai_api_key
    )
    tools = load_tools(
        tool_names=["serpapi", "llm-math"],
        serpapi_api_key=args.serpapi_api_key,
        llm=llm
    )

    agent = initialize_agent(
        tools=tools,
        llm=chat,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    result: str = agent.run("Who is Olivia Wilde's boyfriend? What is his current age raised to the 0.23 power?")
    print(result)

    return


if __name__ == '__main__':
    # demo1()
    demo2()
