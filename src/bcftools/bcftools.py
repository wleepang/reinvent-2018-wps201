#!/usr/bin/env python
"""
wrapper for bcftools that writes outputs generated to a specified S3 bucket
"""

import os
import argparse
import subprocess

import boto3

parser = argparse.ArgumentParser()
parser.add_argument(
    "--s3-output",
    type=str,
    help="""
        S3 url for results output
    """
)
parser.add_argument(
    "--bcftools-args",
    required=True,
    type=str,
    help="""
        Arguments passed to bcftools __excluding__ the input vcf file
        and any output arguments (i.e. --output-*)
    """
)
parser.add_argument(
    "--vcf-input",
    required=True,
    type=str,
    help="""
        Input VCF file (with optional GZIP compression).
        Passed directly to bcftools.
    """
)

def main(args):
    output_args = []
    output_file = None
    if args.s3_output:
        output_file = os.path.basename(args.s3_output)
        output_args = [
            "-o", output_file,
            "-Oz"
        ]

    proc = subprocess.run(
        ["bcftools"] + args.bcftools_args.split() + output_args + [args.vcf_input],
        check=True
    )

    if proc.returncode == 0:
        if args.s3_output and output_file:
            s3 = boto3.client("s3")
            
            bucket, *key = args.s3_output.replace("s3://", "").split("/")
            key = "/".join(key)

            with open(output_file, 'rb') as data:
                s3.upload_fileobj(data, bucket, key)


if __name__ == '__main__':
    main(parser.parse_args())