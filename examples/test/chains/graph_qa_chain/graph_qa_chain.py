#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
这个非常不准.
"""
import argparse

from langchain.indexes import GraphIndexCreator
from langchain.llms import OpenAI
from langchain.document_loaders import TextLoader
from langchain.graphs.networkx_graph import KnowledgeTriple
from langchain.chains.graph_qa.cypher import GraphCypherQAChain
from langchain.graphs.neo4j_graph import Neo4jGraph
from langchain.graphs.networkx_graph import NetworkxEntityGraph
from langchain.chains.llm import LLMChain
from langchain.chains.graph_qa.prompts import PROMPT, CYPHER_GENERATION_PROMPT

import project_settings as settings


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        default="鼻炎是怎么导致的",
        type=str
    )

    parser.add_argument("--kg_url", default="neo4j://localhost", type=str)
    parser.add_argument("--database", default="medical", type=str)
    parser.add_argument("--username", default="neo4j", type=str)
    parser.add_argument("--password", default="Glory@2021!", type=str)

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
        openai_api_key=args.openai_api_key,
        verbose=True,
    )

    # graph
    graph = Neo4jGraph(
        url=args.kg_url,
        username=args.username,
        password=args.password,
        database=args.database,
    )
    graph.refresh_schema()
    # print(graph.schema)

    # llm chain
    qa_chain = LLMChain(llm=llm, prompt=PROMPT)
    cypher_generation_chain = LLMChain(
        llm=llm,
        prompt=CYPHER_GENERATION_PROMPT
    )

    # chain
    chain = GraphCypherQAChain(
        graph=graph,
        cypher_generation_chain=cypher_generation_chain,
        qa_chain=qa_chain,
        verbose=True,
    )

    result = chain.run(args.query)
    print(result)

    return


if __name__ == '__main__':
    main()
