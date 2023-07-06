#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from typing import List

from project_settings import project_path
from toolbox.os.environment import EnvironmentManager
from toolbox.os.other import pwd

pwd = pwd()

log_directory = os.path.join(pwd, 'logs')
os.makedirs(log_directory, exist_ok=True)

temp_directory = os.path.join(pwd, 'temp')
os.makedirs(temp_directory, exist_ok=True)

static_directory = os.path.join(pwd, 'static')
os.makedirs(static_directory, exist_ok=True)

pdf_directory = os.path.join(static_directory, 'pdf')
os.makedirs(pdf_directory, exist_ok=True)

pretrained_models_directory = os.path.join(project_path, 'pretrained_models')
os.makedirs(pretrained_models_directory, exist_ok=True)


environment = EnvironmentManager(
    path=os.path.join(project_path, 'dotenv'),
    env=os.environ.get('environment', 'dev'),
)

port = environment.get(key='port', default=9380, dtype=int)

openai_api_key = environment.get(key='openai_api_key', default='openai_api_key', dtype=str)
hf_api_token = environment.get(key='hf_api_token', default='hf_api_token', dtype=str)

# embedding
hf_embedding_repo_id = environment.get(key='hf_embedding_repo_id', default='sentence-transformers/all-mpnet-base-v2', dtype=str)

# llm
# hf_llm_repo_id = environment.get(key='hf_llm_repo_id', default='jondurbin/airoboros-33b-gpt4-1.4', dtype=str)
hf_llm_repo_id = environment.get(key='hf_llm_repo_id', default='gpt2', dtype=str)


if __name__ == '__main__':
    pass
