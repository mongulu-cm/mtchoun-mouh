#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import os
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr

# Source: https://github.com/gzog/python-dynamodb-copy-table-data
"""
To fill your links databases with current state of prod database

BRANCH=$(git branch --show-current)
python copy_table.py -src Link_table -dest $BRANCH-Link_table

"""

parser = argparse.ArgumentParser(
    description='Copy data from src DynamoDB table to dest')
parser.add_argument('-src', help='source table name', required=True)
parser.add_argument('-dest', help='destination table name', required=True)
parser.add_argument(
    '-src_profile', help='source profile to use', required=False)
parser.add_argument(
    '-dest_profile', help='destination profile to use', required=False)

args = parser.parse_args()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""

    for i in range(0, len(l), n):
        yield l[i:i + n]


REGION_NAME = os.environ.get('AWS_DEFAULT_REGION', 'eu-central-1')
SOURCE_TABLE_NAME = args.src
DESTINATION_TABLE_NAME = args.dest

if args.src_profile:
    src_session = boto3.session.Session(profile_name=args.src_profile)
    src_client = src_session.client('dynamodb', region_name=REGION_NAME)
else:
    src_client = boto3.client('dynamodb', region_name=REGION_NAME)

if args.dest_profile:
    dest_session = boto3.session.Session(profile_name=args.dest_profile)
    dest_client = dest_session.client('dynamodb', region_name=REGION_NAME)
else:
    dest_client = boto3.client('dynamodb', region_name=REGION_NAME)

last_evaluated_key = True
chunk_idx = 0
total_items = 0

while last_evaluated_key:
    if type(last_evaluated_key) == bool:
        response = src_client.scan(TableName=SOURCE_TABLE_NAME)
    else:
        response = src_client.scan(TableName=SOURCE_TABLE_NAME,
                                   ExclusiveStartKey=last_evaluated_key)

    for chunk in chunks(response['Items'], 25):
        total_items += len(chunk)
        chunk_idx += 1

        batch_write = {DESTINATION_TABLE_NAME: []}

        for item in chunk:
            batch_write_item = {'PutRequest': {'Item': {}}}

            for (k, v) in item.items():
                batch_write_item['PutRequest']['Item'][k] = v

            batch_write[DESTINATION_TABLE_NAME].append(batch_write_item)
        dest_client.batch_write_item(RequestItems=batch_write)

        print(f'Written chunk: {chunk_idx}')
    last_evaluated_key = response.get('LastEvaluatedKey', None)
    print(f'Last Evaluated Key: {last_evaluated_key}')

print(f'Total items copied: {total_items}')
