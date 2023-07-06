#!/usr/bin/python3
# -*- coding: utf-8 -*-


doc_qa_request_schema = {
    'type': 'object',
    'required': ['engine_name', 'file_url', 'query', 'top_k', 'chunk_size', 'chunk_overlap'],
    'properties': {
        'engine_name': {
            'type': 'string',
        },
        'file_url': {
            'type': 'string',
        },
        'query': {
            'type': 'string',
        },
        'top_k': {
            'type': 'string',
        },
        'chunk_size': {
            'type': 'string',
        },
        'chunk_overlap': {
            'type': 'string',
        },
    }
}


if __name__ == '__main__':
    pass
