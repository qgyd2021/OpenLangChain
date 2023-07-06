#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import os
from typing import List

from flask import render_template, request
import jsonschema
import requests

from server.exception import ExpectedError
from server.flask_server.route_wrap.common_route_wrap import common_route_wrap
from server.doc_qa_server import settings
from server.doc_qa_server.schema import mrc as mrc_schema
from server.doc_qa_server.service.mrc import engine_to_chain, DocQA
from toolbox.logging.misc import json_2_str


logger = logging.getLogger('server')


def mrc_page():
    return render_template("mrc.html")


@common_route_wrap
def get_choice_of_engine() -> List[str]:
    return list(engine_to_chain.keys())


@common_route_wrap
def mrc_chain():
    args = request.form
    logger.info('mrc_chain, args: {}'.format(json_2_str(args)))

    # request body verification
    try:
        jsonschema.validate(args, mrc_schema.mrc_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    engine_name = args['engine_name']
    query = args['query']
    documents = args['documents']

    if engine_name not in engine_to_chain.keys():
        raise ExpectedError(
            status_code=60401,
            message='file type invalid.',
        )

    chain: DocQA = engine_to_chain[engine_name]
    result: str = chain.search(documents=documents, query=query)
    return result


if __name__ == '__main__':
    pass
