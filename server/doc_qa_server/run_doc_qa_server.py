#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys

pwd = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(pwd, '../../'))

from flask import Flask
from gevent import pywsgi

from server import log
from server.doc_qa_server import settings
log.setup(log_directory=settings.log_directory)

from server.doc_qa_server.view_func import single_doc_qa
from server.doc_qa_server.view_func import mrc
from server.flask_server.view_func.heart_beat import heart_beat

logger = logging.getLogger("server")


# 初始化服务
flask_app = Flask(
    __name__,
    static_url_path="/",
    static_folder="static",
    template_folder="static/templates",
)

flask_app.add_url_rule(rule="/HeartBeat", view_func=heart_beat, methods=["GET", "POST"], endpoint="HeartBeat")
flask_app.add_url_rule(rule="/single_doc_qa", view_func=single_doc_qa.single_doc_qa_page, methods=["GET"], endpoint="SingleDocQAPage")
flask_app.add_url_rule(rule="/single_doc_qa/get_choice_of_engine", view_func=single_doc_qa.get_choice_of_engine, methods=["GET"], endpoint="SingleDocQAGetChoiceOfEngine")
flask_app.add_url_rule(rule="/single_doc_qa/retrieval_qa_chain", view_func=single_doc_qa.retrieval_qa_chain, methods=["POST"], endpoint="SingleDocQARetrievalQA")

flask_app.add_url_rule(rule="/mrc", view_func=mrc.mrc_page, methods=["GET"], endpoint="MRCPage")
flask_app.add_url_rule(rule="/mrc/get_choice_of_engine", view_func=mrc.get_choice_of_engine, methods=["GET"], endpoint="MRCGetChoiceOfEngine")
flask_app.add_url_rule(rule="/mrc/mrc_chain", view_func=mrc.mrc_chain, methods=["POST"], endpoint="MRCChain")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        default=settings.port,
        type=int,
    )
    args = parser.parse_args()

    logger.info("model server is already, 127.0.0.1:{}".format(args.port))

    # flask_app.run(
    #     host='0.0.0.0',
    #     port=args.port,
    # )

    server = pywsgi.WSGIServer(
        listener=("0.0.0.0", args.port),
        application=flask_app
    )
    server.serve_forever()
