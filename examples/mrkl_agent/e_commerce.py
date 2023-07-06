#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse

from langchain.agents import Tool
from langchain.agents.agent import Agent, AgentExecutor
from langchain.agents.mrkl.output_parser import MRKLOutputParser
from langchain.chains import LLMChain
from langchain.llms import OpenAI, HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish, OutputParserException
# from langchain.agents.mrkl.prompt import PREFIX, FORMAT_INSTRUCTIONS, SUFFIX
from langchain.agents.mrkl.base import ZeroShotAgent, MRKLChain
from langchain.tools.base import ToolException

import project_settings as settings


DEFAULT_QUERY_LIST = [
    "我想买一个iPhone，但是不知道哪个款式好，你能帮我推荐一下吗？",
    "我有一张订单，订单号是 6fff58ba-f13c-4c6e-92a0-5182b31fb1f0，一直没有收到，能麻烦帮我查一下吗？",
    "请问你们的货，能送到格尔木吗？大概需要几天？",
    "今天会不会下雨啊？",
]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY_LIST[0],
        type=str
    )
    parser.add_argument(
        "--openai_api_key",
        default=settings.environment.get("openai_api_key", default=None, dtype=str),
        type=str
    )
    args = parser.parse_args()
    return args


PREFIX = """尽可能回答以下问题. 您可以使用以下工具: """


SUFFIX = """你是一家电商网站的客服, 你的名字叫 OpenAI Chain. 
请你回答用户的问题, 如果不能确定答案, 请回答不知道, 不要编造答案. 
不要过度思考, 尽可能提前停止. 
开始!

Question: {input}
Thought: {agent_scratchpad}"""


FORMAT_INSTRUCTIONS = """使用以下格式: 

Question: 您必须回答的输入问题
Thought: 你应该时刻思考该做什么
Action: 要采取的操作, 应该是 [{tool_names}] 之一
Action Input: Action 的输入, 其取值, 应该参考 tool 的描述. 
Observation: Action 的结果
...(这个 Thought/Action/Action Input/Observation 可以重复 N 次) 
Thought: 我现在知道了最终答案
Final Answer: 原始输入问题的最终答案
"""


USER_INFO = """"""

USER_ORDER_LIST = """
商品名称: iPhone 14 Pro
商品品牌: 苹果
商品品类: 手机
订单号: 6fff58ba-f13c-4c6e-92a0-5182b31fb1f0
订单状态：已发货
发货日期：2023-01-01
预计送达时间：2023-01-10


商品名称: MacBook Pro 13
商品品牌: 苹果
商品品类: 笔记本电脑
订单号: fa62227a-313b-4321-9a4e-bdcb770e8e84
订单状态：未付款
发货日期：付款后1-2个工作日之后. 
预计送达时间：发货后3-7个工作日之后. 

"""

PRODUCT_INFO = {
    "iphone 14 pro": """
商品名称: iPhone 14 Pro
商品品牌: 苹果
商品品类: 手机

商品毛重：377.00g
商品产地：中国大陆
CPU型号：A16
运行内存：6GB
机身颜色：深空黑色
三防标准：IP68
充电功率：25W及以下
机身内存：256GB
风格：苹果风
屏幕材质：OLED直屏
后摄主像素：普通(以官网信息为准)
机身色系：黑色系

""",
    "iphone 13 pro max": """
商品名称：iPhone 13 Pro Max
商品编号：10070791073061
商品毛重：1.0kg
CPU型号：A15
运行内存：6GB
机身颜色：远峰蓝色
三防标准：IP68
屏幕分辨率：FHD+
充电功率：25W及以下
机身内存：128GB
机身色系：浅蓝色系
屏幕材质：OLED直屏
后摄主像素：1200万像素
风格：简约风，大气，IP

""",
    "macbook pro 13": """
商品名称：MacBook Pro 13
商品品牌: 苹果
商品品类: 笔记本电脑

商品编号：100026923531
商品毛重：2.7kg
商品产地：中国大陆
内存容量：16GB
系列：Apple-MacBook Pro
屏幕色域：100%sRGB
颜色：深空灰色
类型：轻薄笔记本
显卡芯片供应商：Apple
系统：MacOS
支持IPv6：支持
IPv6处理器：Apple M2
屏幕刷新率：60Hz
屏幕尺寸：13.0-13.9英寸
屏幕比例：16:10
显卡型号：Apple M2
集成显卡厚度：15.1-18.0mm
固态硬盘（SSD）：512GB
机械硬盘：无机械硬盘
""",
    "macbook air 13.3": """
商品名称：AppleMGND3CH/A
商品编号：100026406616
商品毛重：2.37kg
商品产地：中国大陆
内存容量：8GB
系列：Apple-MacBook Air
屏幕色域：DCI-P3
机械硬盘：无机械硬盘
支持IPv6：支持IPv6
固态硬盘（SSD）：256GB
系统：MacOS
屏幕尺寸：13.0-13.9英寸
厚度：15.1-18.0mm
屏幕刷新率：60Hz
类型：轻薄笔记本
处理器：Apple M1
显卡型号：APPLE M1 集成显卡
屏幕比例：16:10
显卡芯片供应商：Apple
颜色：金色

""",
}

RECOMMEND_PRODUCT_LIST = {
    "手机": """
iPhone 14 Pro
iPhone 13 Pro Max
""",
    "笔记本电脑": """
MacBook Pro 13
MacBook Air 13.3
"""
}


DELIVERY_RANGE = """
格尔木, 15-20天
美国, 3-7天
英语, 3-7天
刚果, 15-20天
"""


def chat(query: str = None):
    return "final answer 回答: 你好, 我叫 OpenAI Chain, 有什么可以帮助你的吗. 然后结束. "


def search_user_order_list(username: str):
    return USER_ORDER_LIST


def search_product_info(product_name: str):
    product_name = str(product_name).strip().lower()
    return PRODUCT_INFO.get(product_name, "未找到该商品的信息.")


def search_recommend_product(category: str):
    category = str(category).strip().lower()
    return RECOMMEND_PRODUCT_LIST.get(category, "未找到该品类的商品, 支持的品类是: 手机, 笔记本电脑.")


def search_delivery_range(query: str = None):
    return DELIVERY_RANGE


def main():
    args = get_args()

    tools = [
        Tool(
            name="Chat", func=chat,
            description="用这个工具与用户进行闲聊互动. Action Input 一律为 None. ",
            handle_tool_error=False,
        ),
        Tool(
            name="User Order List", func=search_user_order_list,
            description="用这个工具查询用户的订单列表, 包括已发货, 未发货, 未付款等订单, Action Input 为商品名称, 商品品类或 None. ",
            handle_tool_error=True,
        ),
        Tool(
            name="Search Product Info", func=search_product_info,
            description="用这个工具查询商品信息, 包括商品重量, 商品价格, 等商品详细信息. Action Input 为商品名称. ",
            handle_tool_error=True,
        ),
        Tool(
            name="Search Recommend Product", func=search_recommend_product,
            description="用这个工具为用户推荐商品, Action Input 为商品品类, 例如: 手机, 笔记本电脑. ",
            handle_tool_error=True,
        ),
        Tool(
            name="Delivery Range", func=search_delivery_range,
            description="用这个工具查询送货范围, Action Input 一律为 None. ",
            handle_tool_error=False,
        ),
    ]

    # llm
    llm = OpenAI(
        temperature=0.9,
        openai_api_key=args.openai_api_key
    )

    # prompt
    prompt: PromptTemplate = ZeroShotAgent.create_prompt(
        tools=tools,
        prefix=PREFIX,
        suffix=SUFFIX,
        format_instructions=FORMAT_INSTRUCTIONS,
        input_variables=["input", "agent_scratchpad"]
    )

    # llm chain
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    output_parser = MRKLOutputParser()

    agent: ZeroShotAgent = ZeroShotAgent(
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

    while True:
        query = input("query: ")
        if query == "Quit":
            break
        agent_executor.run({'input': query})
    return


if __name__ == '__main__':
    main()
