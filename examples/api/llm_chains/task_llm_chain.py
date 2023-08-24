#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import re

from langchain.chains.llm import LLMChain
from langchain.llms import OpenAI, HuggingFaceHub
from langchain.prompts import PromptTemplate

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


TEMPLATE = """
我们需要从用户查询中提取关键信息, 如下: 

QueryType: 疑问句类型, 一般包括: 疑问(能否), 疑问(哪个), 疑问(是否), 疑问(吗), 疑问(多少), 
疑问(为何), 疑问(什么), 疑问(如何), 疑问(哪里), 疑问(地址), 疑问(是什么), 疑问(姓名), 
疑问(有没有), 疑问(A还是B), 疑问(哪位), 疑问(哪些), 疑问(时间), 疑问(没有), 疑问(怎么了), 
疑问(时长), 疑问(怎么办). 
只使用给定的这些标签类别, 无法确定时用 None 填充. 

QuerySubject: 查询主题, 一般是名词. 无法确定时用 None 填充. 

QueryAction: 查询动作, 一般是动词. 无法确定时用 None 填充. 


例如: 
Query: NXLink的嵌入式注册流程. 
QueryType: (疑问)是什么
QuerySubject: 注册流程
QueryAction: None

Query: 怎样创建客服团队.
QueryType: (疑问)如何
QuerySubject: 客服团队
QueryAction: 创建

Query: DID号码怎么购买. 
QueryType: (疑问)如何
QuerySubject: DID号码
QueryAction: 购买

Query: 在哪里查看对话记录. 
QueryType: (疑问)哪里
QuerySubject: 对话记录
QueryAction: 查看

Query: 无条件退款是多长时间. 
QueryType: (疑问)时长
QuerySubject: 无条件退款
QueryAction: None

Query: whatsapp消息模板审核不通过. 
QueryType: 疑问(为何)
QuerySubject: whatsapp消息模板审核
QueryAction: 不通过

Query: {query}
QueryType:
"""


def main():
    args = get_args()

    llm = OpenAI(
        temperature=0.9,
        openai_api_key=args.openai_api_key
    )
    prompt: PromptTemplate = PromptTemplate.from_template(TEMPLATE)

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    print(prompt.input_variables)

    # query = "怎么迁移whatsapp 号码. "
    # query = "whatsapp消息模板分为哪几类. "
    query = "公司执照审核没通过.  "
    # query = "facebook账号注册有哪些注意事项. "
    # query = "注册网站建设的参考建议. "
    outputs = llm_chain.predict(query=query)

    # print(outputs)
    # print(type(outputs))
    # print(len(outputs))

    pattern = r"\s*(.+)\s*QuerySubject:\s*(.+)\s*QueryAction:\s*(.+)\s*"

    match = re.search(pattern, outputs, flags=re.IGNORECASE)
    print("-" * 150)
    print(match.group(0))
    print("-" * 150)
    print(match.group(1))
    print(match.group(2))
    print(match.group(3))
    return


if __name__ == '__main__':
    main()
