#!/usr/bin/env bash

rm -rf nohup.out
rm -rf logs/

source /data/local/bin/OpenLangChain/bin/activate

nohup python3 run_doc_qa_server.py > nohup.out &
