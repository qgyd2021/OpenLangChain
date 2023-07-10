#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import json
import logging

from toolbox.neo4j.neo4j_restful import Neo4jRestful


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--database", default="medical", type=str)
    parser.add_argument("--username", default="neo4j", type=str)
    parser.add_argument("--password", default="Glory@2021!", type=str)

    parser.add_argument(
        "--statement",
        default="""MATCH (x:Disease { name: "感冒" }) RETURN x.cause""",
        type=str
    )

    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    return args


def main():
    args = get_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    neo4j_restful = Neo4jRestful(
        database=args.database,
        username=args.username,
        password=args.password,
    )

    print(args.statement)
    result = neo4j_restful.cmd(statements=args.statement, do_commit=True, retry_to_ensure_success=False)
    print(result)
    return


if __name__ == '__main__':
    main()
