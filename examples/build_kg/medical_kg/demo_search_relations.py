#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import logging

import pandas as pd

from toolbox.neo4j.neo4j_restful import Neo4jRestful
from toolbox.neo4j.converters import escape_string


# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )

neo4j_restful = Neo4jRestful(
    database='neo4j',
    username='neo4j',
    password='Glory@2021!'
)


def demo1():
    """科室总结"""
    # mention = 'Check'
    # mention = 'Department'
    # mention = 'Disease'
    # mention = 'Drug'
    # mention = 'Food'
    # mention = 'Producer'
    mention = 'Symptom'

    statement = """
    MATCH (x:{mention}) RETURN x
    """.format(mention=mention)
    js = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

    results = js['results']

    synonyms_list = list()
    for result in results:
        data = result['data']

        for row in data:
            departments = row['row']
            for department in departments:
                department = department['name']

                synonyms_list.append({
                    'standard': department,
                    'synonyms': department
                })

    synonyms_list = pd.DataFrame(synonyms_list)
    synonyms_list = synonyms_list.sort_values(by=['standard', 'synonyms'])
    synonyms_list.to_excel('{}.xlsx'.format(mention.lower()), index=False, encoding='utf_8_sig')
    return


def demo2():
    """科室层级关系"""
    # 查找所有的一级科室
    statement = """
    MATCH (x:Department)-[r:belongs_to]->(y:Department) RETURN y
    """
    print(statement)
    js1 = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

    results1 = js1['results']

    hierarchical_departments_list = list()

    unique_department1 = set()
    for result1 in results1:
        data1 = result1['data']
        for row1 in data1:
            departments1 = row1['row']
            for department1 in departments1:
                department1 = department1['name']
                if department1 in unique_department1:
                    continue
                unique_department1.add(department1)

                statement = """
                MATCH (x:Department)-[r:belongs_to]->(y:Department {{ name: "{department1}" }}) RETURN x
                """.format(department1=department1)
                js2 = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)
                results2 = js2['results']

                for result2 in results2:
                    data2 = result2['data']
                    for row2 in data2:
                        departments2 = row2['row']
                        for department2 in departments2:
                            department2 = department2['name']

                            hierarchical_departments_list.append({
                                'department1': department1,
                                'department2': department2
                            })

    hierarchical_departments_list = pd.DataFrame(hierarchical_departments_list)
    hierarchical_departments_list = hierarchical_departments_list.sort_values(by=['department1', 'department2'])
    hierarchical_departments_list.to_excel('hierarchical_departments_list.xlsx', index=False, encoding='utf_8_sig')
    return


if __name__ == '__main__':
    demo1()
    # demo2()
