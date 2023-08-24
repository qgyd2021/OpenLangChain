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
请从以下文本段落中提取实体. 


ExampleContext: 
------
## 3步快速使用NXLink（入门必读）

https://help.nxcloud.com/nxlink/docs/qOtoWc


### 第1步：注册NXLink系统账号

每个公司只需要注册一个账号即可，其余账号通过邀请方式加入


### 第2步：配置WhatsApp号码

#### 1）准备注册资料

配置WhatsApp号码（这个过程也叫嵌入式注册）之前，需要先准备好嵌入式注册的相关资料

#### 2）完成嵌入式注册

登录NXLink系统，找到配置---消息通道---配置WhatsApp号码，完成操作


### 第3步：完成meta企业认证

嵌入式注册完成后，还需要完成meta的企业认证

------

ExampleEntity: "NXLink系统账号"; "WhatsApp号码"; "嵌入式注册"; "NXLink系统"; "配置"; "消息通道"; "meta企业认证";


Context: 
------
{context}
------

Entity:
"""

context = """
#### 步骤4：创建WABA

**注册新的WABA**：填写WABA名称、号码显示名称、业务类型和公司简介。

如果是注册在现有的WABA下，直接选择对应的WABA即可。

**号码显示名称，建议输入公司品牌名称，或与公司名称，网站域名相关的名称（相关内容需要在网站上需体现），否则可能无法通过审核！**


"""


def main():
    args = get_args()

    llm = OpenAI(
        temperature=0.9,
        openai_api_key=args.openai_api_key,
        max_tokens=512,
    )
    prompt: PromptTemplate = PromptTemplate.from_template(TEMPLATE)

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    print(prompt.input_variables)

    outputs = llm_chain.predict(context=context)
    print(outputs)

    return


if __name__ == '__main__':
    main()
