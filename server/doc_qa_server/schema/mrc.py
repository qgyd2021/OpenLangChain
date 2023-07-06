#!/usr/bin/python3
# -*- coding: utf-8 -*-


mrc_request_schema = {
    'type': 'object',
    'required': ['engine_name', 'query', 'documents'],
    'properties': {
        'engine_name': {
            'type': 'string',
        },
        'query': {
            'type': 'string',
        },
        'documents': {
            'type': 'string',
        },
    }
}


if __name__ == '__main__':
    pass
