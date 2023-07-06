#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse

from langchain.utilities.serpapi import SerpAPIWrapper

import project_settings as settings


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        default="What products does NXCloud company provide ?",
        type=str
    )
    parser.add_argument(
        "--serpapi_api_key",
        default=settings.environment.get("serpapi_api_key", default=None, dtype=str),
        type=str
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    serpapi = SerpAPIWrapper(
        serpapi_api_key=args.serpapi_api_key,
    )

    result: str = serpapi.run(args.query)
    print(result)
    return


if __name__ == '__main__':
    main()
