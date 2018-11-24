#!/usr/bin/env python
"""
Example of invoking a SageMaker endpoint from an application
"""

import io
import json
import argparse
from pprint import pprint
from configparser import ConfigParser

import boto3


parser = argparse.ArgumentParser()

parser.add_argument(
    '--profile',
    dest='profile_name',
    help='AWS profile'
)

parser.add_argument(
    '--region',
    dest='region_name',
    help='AWS region'
)

parser.add_argument(
    'data_file'
)


def main(args):
    session = boto3.Session(
        profile_name=args.profile_name, 
        region_name=args.region_name)
    
    smrt = session.client('sagemaker-runtime')

    config_parser = ConfigParser()
    config_parser.read(['config.ini'])
    config = config_parser['DEFAULT']

    with open(args.data_file, 'rb') as body:
        try:
            response = smrt.invoke_endpoint(
                EndpointName=config['endpoint'],
                Body=body,
                ContentType='text/csv',
                Accept='application/json'
            )

            result = {
                'endpoint': config['endpoint'],
                'request_id': response['ResponseMetadata']['RequestId'],
                'predictions': json.loads(
                    response['Body'].read().decode('utf-8')
                )['predictions']
            }
            pprint(result)
            
        except Exception as e:
            print(e)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)