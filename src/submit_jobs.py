#!/usr/bin/env python3
"""
script to submit jobs to AWS Batch to get features for modeling
from the 1000 genomes public dataset
"""

import os
import re
import argparse

import boto3

parser = argparse.ArgumentParser()

parser.add_argument(
    "--profile", 
    type=str, 
    default=None,
    help="""
        AWS profile to use instead of \"default\". Create one using the AWS 
        CLI e.g. aws configure --profile <profile>
    """
)

parser.add_argument(
    "--region",
    dest="region_name",
    type=str,
    help="""
        AWS region name to use when creating resources.  
        If not specified, uses the configured default region for the current 
        profile.  See: \"aws configure\".
    """
)

# creates a mapping of the source vcf files from the 1000genomes public dataset
# to the processed vcf file produced from the batch pipeline
# Example:
#  {'chr1.freq60.biallelic.snps.vcf.gz': 'ALL.chr1.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz',
#   'chr10.freq60.biallelic.snps.vcf.gz': 'ALL.chr10.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz',
#   ... }
S3 = boto3.resource('s3')
BUCKET = "1000genomes"
PREFIX = "release/20130502"
PROCESSING = "freq60.biallelic.snps"
VCF_FILES = {
    re.sub(
        '^.*?(chr[0-9XY]+|wgs).*?(vcf.gz)$',
        f'\\1.{PROCESSING}.\\2',
        vcf_file
    ) : vcf_file
    for vcf_file in [
        os.path.basename(o.key)
        for o in S3.Bucket(BUCKET).objects.filter(Prefix=PREFIX)
        if o.key.endswith('.vcf.gz') and os.path.dirname(o.key) == PREFIX
]}


S3_OUTPUT = "s3://pwyming-wps201-us-east-1/data"
QUEUE_ARN = "arn:aws:batch:us-east-1:402873085799:job-queue/wps201-queue"


def s3path(s3url):
    bucket, *key = s3url.replace("s3://", "").split("/")
    return {
        "bucket": bucket,
        "key": os.path.join(*key)
    }


def vcf_filter(session):
    batch = session.client("batch")

    job_def = batch.register_job_definition(
        jobDefinitionName='wps201_vcf_filter',
        type='container',
        containerProperties={
            'image': 'oddhypothesis/bcftools:1.9-aws',
            'vcpus': 2,
            'memory': 4096
        }
    )
    print(f'[job definition registered] : {job_def["jobDefinitionArn"]}')

    job_ids = dict()
    for target, source in VCF_FILES.items():
        command = [
            "--s3-output", f"{S3_OUTPUT}/{target}",
            "--bcftools-args", "view -m2 -M2 -q 0.6 -v snps",
            "--vcf-input", f"s3://1000genomes/release/20130502/{source}",
        ]

        try:
            response = batch.submit_job(
                jobName = target.replace(".vcf.gz", "").replace(".", "-"),
                jobQueue = QUEUE_ARN,
                jobDefinition = job_def['jobDefinitionArn'],
                containerOverrides = {
                    "command": command
                }
            )

            print(f"[{response['jobId']}] : {target} : {command}")
            job_ids[target] = response['jobId']
        
        except Exception as e:
            job_ids[target] = None
            print(f"[job submission failed] : {target} : {e}")
        
    return job_ids


def feature_filter(session, input_ids=None):
    s3 = session.resource('s3')
    batch = session.client('batch')

    if input_ids:
        # the vcf_files will be the keys of input_ids
        vcf_files = input_ids.keys()
    else:
        # list the data bucket for files to process
        bucket = s3.Bucket(s3path(S3_OUTPUT)['bucket'])
        vcf_files = [
            os.path.basename(o.key) 
            for o in bucket.objects.filter(Prefix='data') 
            if o.key.endswith('.vcf.gz')
        ]

    job_def = batch.register_job_definition(
        jobDefinitionName='wps201_feature_filter',
        type='container',
        containerProperties={
            'image': 'oddhypothesis/allel:latest',
            'vcpus': 2,
            'memory': 4096
        }
    )
    print(f'[job definition registered] : {job_def["jobDefinitionArn"]}')

    job_ids = dict()
    for vcf_file in vcf_files:
        command = [
            "--s3-output-path", S3_OUTPUT,
            "--sample-method", "first", 
            "--sample-n", "100",
            os.path.join(S3_OUTPUT, vcf_file)
        ]

        try:
            depends_on = None
            if input_ids:
                if input_ids[vcf_file]:
                    depends_on = [{
                        'jobId': input_ids[vcf_file],
                        'type': 'SEQUENTIAL'
                    }]
            
            response = batch.submit_job(
                jobName = vcf_file.replace(".vcf.gz", ".first100").replace(".", "-"),
                jobQueue = QUEUE_ARN,
                jobDefinition = job_def['jobDefinitionArn'],
                dependsOn = depends_on,
                containerOverrides = {
                    "command": command
                }
            )

            print(f"[{response['jobId']}] : {vcf_file} : {command}")
            job_ids[vcf_file] = response['jobId']
        
        except Exception as e:
            job_ids[vcf_file] = None
            print(f"[job submission failed] : {vcf_file} : {e}")
    
    return job_ids


def main(args):
    session = boto3.Session(profile_name=args.profile, region_name=args.region_name)
    
    job_ids = vcf_filter(session)
    feature_filter(session, input_ids=job_ids)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)

