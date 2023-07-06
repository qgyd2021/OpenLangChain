#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
from typing import Union

from langchain.agents.mrkl.output_parser import MRKLOutputParser
from langchain.schema import AgentAction, AgentFinish, OutputParserException


DEFAULT_TEXT1 = """
Action: Calculator
Action Input: 57^.023
"""


DEFAULT_TEXT2 = """
Final Answer: The high temperature in SF yesterday in Fahrenheit raised to the .023 power is 1.0974509573251117.
"""


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--text",
        default=DEFAULT_TEXT1,
        type=str
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    output_parser = MRKLOutputParser()

    result: Union[AgentAction, AgentFinish] = output_parser.parse(args.text)

    if isinstance(result, AgentAction):
        print(result.tool)
        print(result.tool_input)
        print(result.log)
    elif isinstance(result, AgentFinish):
        print(result.return_values)
        print(result.log)
    else:
        raise AssertionError
    return


if __name__ == '__main__':
    main()
