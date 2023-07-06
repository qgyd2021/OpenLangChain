#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse

from langchain.agents import initialize_agent, Tool
from langchain.agents.agent import Agent, AgentExecutor
from langchain.llms import OpenAI

import project_settings as settings


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        default="What products does NXCloud company provide ?",
        type=str
    )
    parser.add_argument(
        "--openai_api_key",
        default=settings.environment.get("openai_api_key", default=None, dtype=str),
        type=str
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    # llm
    llm = OpenAI(
        temperature=0.9,
        openai_api_key=args.openai_api_key
    )

    def search_order(query: str) -> str:
        return "订单状态：已发货；发货日期：2023-01-01；预计送达时间：2023-01-10"

    def recommend_product(query: str) -> str:
        return "iPhone 15 Pro"

    def faq(query: str) -> str:
        return "7天无理由退货"

    tools = [
        Tool(
            name="Search Order", func=search_order,
            description="useful for when you need to answer questions about customers orders"
        ),
        Tool(
            name="Recommend Product", func=recommend_product,
            description="useful for when you need to answer questions about product recommendations"
        ),
        Tool(
            name="FAQ", func=faq,
            description="useful for when you need to answer questions about shopping policies, like return policy, shipping policy, etc."
        )
    ]

    agent_executor: AgentExecutor = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
    agent_executor.run({'input': "我买的手机什么时候发货啊. 这个应该是无理由退货的吧?"})
    return


if __name__ == '__main__':
    main()
