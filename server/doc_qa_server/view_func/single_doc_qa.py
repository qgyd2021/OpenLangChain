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
from server.doc_qa_server.schema import doc_qa
from server.doc_qa_server.service.doc_qa import engine_to_chain, DocQA
from toolbox.logging.misc import json_2_str


logger = logging.getLogger('server')


def single_doc_qa_page():
    return render_template("doc_qa.html")


@common_route_wrap
def get_choice_of_engine() -> List[str]:
    return list(engine_to_chain.keys())


@common_route_wrap
def retrieval_qa_chain():
    args = request.form
    logger.info('retrieval_qa_chain, args: {}'.format(json_2_str(args)))

    # request body verification
    try:
        jsonschema.validate(args, doc_qa.doc_qa_request_schema)
    except (jsonschema.exceptions.ValidationError,
            jsonschema.exceptions.SchemaError, ) as e:
        raise ExpectedError(
            status_code=60401,
            message='request body invalid. ',
            detail=str(e)
        )

    # https://arxiv.org/pdf/2203.02155.pdf
    # what's the instruction GPT ?

    engine_name = args['engine_name']
    file_url = args['file_url']
    query = args['query']
    top_k = args['top_k']
    chunk_size = args['chunk_size']
    chunk_overlap = args['chunk_overlap']

    top_k = int(top_k)
    chunk_size = int(chunk_size)
    chunk_overlap = int(chunk_overlap)

    if engine_name not in engine_to_chain.keys():
        raise ExpectedError(
            status_code=60401,
            message='file type invalid.',
        )

    # download file
    _, fn = os.path.split(file_url)
    filename = os.path.join(settings.pdf_directory, fn)
    if not os.path.exists(filename):
        resp = requests.get(file_url)
        with open(filename, 'wb') as f:
            f.write(resp.content)

    # search
    chain: DocQA = engine_to_chain[engine_name]
    outputs = chain.search(filename, query, top_k=top_k, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    result = outputs['result']
    source_documents = outputs['source_documents']
    source_documents = [source_document.page_content for source_document in source_documents]
    source_documents = [source_document.replace('\n', '<br>') for source_document in source_documents]
    source_documents_ = list()
    for idx, source_document in enumerate(source_documents):
        line = ""
        line += "-" * 50
        line += "Document {}".format(idx + 1)
        line += "-" * 50

        source_documents_.append(line)
        source_documents_.append(source_document)

    res = {'result': result, 'source_documents': source_documents_}

    # res = {
    #     'result': 'the instructGPT is good',
    #     'source_documents': [
    #         'GPT GPT\n(prompted)SFT PPO PPO-ptx00.250.500.75PrevalenceAttempts correct instruction\nGPT GPT\n(prompted)SFT PPO PPO-ptx00.10.20.30.40.5Follows explicit',
    #         'GPT GPT\n(prompted)SFT PPO PPO-ptx00.250.500.75PrevalenceAttempts correct instruction\nGPT GPT\n(prompted)SFT PPO PPO-ptx00.10.20.30.40.5Follows explicit',
    #         'GPT GPT\n(prompted)SFT PPO PPO-ptx00.250.500.75PrevalenceAttempts correct instruction\nGPT GPT\n(prompted)SFT PPO PPO-ptx00.10.20.30.40.5Follows explicit',
    #
    #
    #     ]
    # }
    return res


if __name__ == '__main__':
    pass
