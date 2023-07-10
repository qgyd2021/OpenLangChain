#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import logging

from toolbox.neo4j.neo4j_restful import Neo4jRestful

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

neo4j_restful = Neo4jRestful(
    database='neo4j',
    username='neo4j',
    password='Glory@2021!'
)


def demo1():
    name = '感冒'
    statement = """
    MATCH (x:Disease {{ name: "{name}" }}) RETURN x.cause
    """.format(name=name)
    print(statement)
    result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)
    print(result)
    return


def demo2():
    """{label}属于哪个科室"""
    name = '心内科'
    statement = """
    MATCH (x:Department {{ name: "{name}" }})-[r:belongs_to]->(y:Department) RETURN y
    """.format(name=name)
    print(statement)
    result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)
    print(result)
    return


def demo3():
    """
    内科包含哪些科室
    :return:
    """
    name = '内科'
    statement = """
    MATCH (x:Department)-[r:belongs_to]->(y:Department {{ name: "{name}" }}) RETURN x
    """.format(name=name)
    print(statement)
    result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)
    print(result)
    return


def demo4():
    statement = """
    MATCH (x:Department)-[r:belongs_to]->(y:Department) RETURN y
    """
    print(statement)
    result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)
    print(result)
    return


if __name__ == '__main__':
    # demo1()
    # demo2()
    # demo3()
    demo4()
