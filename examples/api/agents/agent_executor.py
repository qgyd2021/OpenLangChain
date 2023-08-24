#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
from datetime import datetime
from typing import Union

from langchain.agents import Tool
from langchain.agents.agent import Agent, AgentExecutor
from langchain.agents.mrkl.output_parser import MRKLOutputParser
from langchain.chains import LLMChain
from langchain.llms import OpenAI, HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.agents.mrkl.prompt import PREFIX, FORMAT_INSTRUCTIONS, SUFFIX
from langchain.agents.mrkl.base import ZeroShotAgent, MRKLChain
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


def main():
    args = get_args()

    def today_date(query: str) -> str:
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        return now_str

    tools = [
        Tool(
            name="Today Date",
            func=today_date,
            description="useful for when you want to know the date of today"
        )
    ]

    # llm
    llm = OpenAI(
        temperature=0.9,
        openai_api_key=args.openai_api_key
    )

    # prompt
    prompt: PromptTemplate = ZeroShotAgent.create_prompt(
        tools=tools,
        prefix=PREFIX, suffix=SUFFIX, format_instructions=FORMAT_INSTRUCTIONS,
        input_variables=["input", "agent_scratchpad"]
    )

    # llm chain
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    output_parser = MRKLOutputParser()

    agent: Agent = ZeroShotAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        allowed_tools=[tool.name for tool in tools]
    )

    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        callback_manager=None,
        tags=["zero-shot-react-description"],
        verbose=True
    )

    inputs = {"input": "what's the date today."}

    agent_executor.run(inputs)
    return


if __name__ == '__main__':
    main()