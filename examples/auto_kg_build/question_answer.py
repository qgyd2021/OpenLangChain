#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import re
from typing import List

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
工程师正在根据说明文档构建问答对. 
给定一段上下文, 你需要提出一个或多个相关的问题, 及其问题对应的答案. 

生成的句子应以 Question/Answer 开头, 如下: 
Question: $YOUR_QUESTION_HERE1. 
Answer: $THE_ANSWER_HERE1. 

Question: $YOUR_QUESTION_HERE2. 
Answer: $THE_ANSWER_HERE2. 

Tips: 
1. 严格根据给定的上下文生成问答对, 不要编造, 如果答案不在上下文中, 请不要提此问题. 
2. 不要生成不明确的笼统的答案. 
3. 生成内容应该是中文, 且每组 Question/Answer 应隔开, 不要包含序号. 
4. Question 应包含全面的信息, 就好像提问时并不知道有上下文的存在. 
5. 

请为以下MarkDown格式的上下文生成指定格式的问题/答案对: 
----------------
{text}
----------------
Question: 
"""


TEXT = """
## 官方商业账号OBA（绿标）申请
...

### WhatsApp官方商业帐号 (OBA)申请步骤
...

#### 操作步骤
...

##### 第二步：提交OBA申请
...

###### 2）提交申请

**申请提交内容：**

点击“提交申请”按钮并填写所需信息。您最多可以提交 5 个支持链接，以展示该公司是知名公司

（1）公司网站：一般输入注册时提供的网站

（2）申请原因：写一些介绍公司如何【优秀】的内容，从哪些地方可以佐证等

（3）链接：添加文章、社交媒体帐户和体现你帐户知名度的其他信息的链接。付费或推广内容不纳入考量。

**知名度说明：**

（1）知名度要求公司代表的是一家搜索频率高的知名品牌或实体。

（2）知名度也反映了公司频频见于各类网络新闻文章。我们根据某个帐号在拥有大量受众的电子刊物新闻文章中的出现频次来评估其知名度。我们不会将付费或促销内容当作新闻来源予以审核，包括公司或应用名录。

"""


def main():
    args = get_args()

    llm = OpenAI(
        temperature=0.7,
        max_tokens=1024,
        n=10,
        openai_api_key=args.openai_api_key
    )
    prompt: PromptTemplate = PromptTemplate.from_template(TEMPLATE)
    # print(prompt.input_variables)

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    print("text length: {}".format(len(TEXT)))

    outputs = llm_chain.predict(text=TEXT)
    print(outputs)
    print("-" * 150)

    pattern = r"\s*(.+)\s*Answer:\s*(.+)\s*"

    outputs_list: List[str] = outputs.split("Question:")
    for output in outputs_list:
        match = re.search(pattern, output, flags=re.IGNORECASE)
        if match is None:
            print("match failed. \noutputs: {}".format(outputs))
            continue
        question = match.group(1)
        answer = match.group(2)

        print("Question: {}".format(question))
        print("Answer: {}".format(answer))
    return


if __name__ == '__main__':
    main()
