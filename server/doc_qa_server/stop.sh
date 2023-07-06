#!/usr/bin/env bash

kill -9 `ps -aef | grep 'run_doc_qa_server.py' | grep -v grep | awk '{print $2}'`

