#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
https://python.langchain.com/docs/modules/chains/popular/sqlite
https://github.com/brunogarcia/langchain-titanic-sqlite
"""
import argparse

from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.chains.llm import LLMChain
from langchain.chains.sql_database.prompt import MYSQL_PROMPT

import project_settings as settings


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        default="How many passengers survived?",
        type=str
    )
    parser.add_argument(
        "--database_uri",
        default="sqlite:///titanic.db",
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

    database = SQLDatabase.from_uri(args.database_uri)

    # llm
    llm = OpenAI(
        temperature=0.9,
        openai_api_key=args.openai_api_key,
        verbose=True,
    )

    # llm chain
    llm_chain = LLMChain(llm=llm, prompt=MYSQL_PROMPT)

    sql_database_chain = SQLDatabaseChain(
        llm_chain=llm_chain,
        database=database,
        prompt=MYSQL_PROMPT,
        verbose=True
    )

    result = sql_database_chain.run(args.query)
    print(result)
    return


if __name__ == '__main__':
    main()
