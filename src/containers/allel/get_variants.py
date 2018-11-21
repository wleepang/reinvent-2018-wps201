"""
Gets High frequency bi-allelic SNPs from a chromosome
"""

import os
import re
import argparse
from tempfile import mkstemp

import boto3
import numpy as np
import pandas as pd
import allel


parser = argparse.ArgumentParser()

parser.add_argument(
    "vcf_file",
    help="VCF file to parse (can be a local or S3 path)"
)

parser.add_argument(
    "--s3-output-path",
    default=None,
    help="S3 path to write results to"
)

parser.add_argument(
    "--sample-method",
    default=None,
    type=str,
    choices=[None, 'first', 'last', 'random'],
    help="Sampling method to apply"
)

parser.add_argument(
    "--sample-n",
    default=None,
    type=int,
    help="Number of records to sample"
)

parser.add_argument(
    "--sample-seed",
    default=None,
    type=int,
    help="Seed for random sampling"
)

def localize(path):
    """
    downloads a file from s3 if needed
    """

    localized_path = path
    if path.lower().startswith('s3://'):
        s3 = boto3.client('s3')

        bucket, *key = path.replace('s3://', '').split('/')
        key = '/'.join(key)

        suffix = None
        if key.endswith('.gz'):
            suffix = '.gz'

        _, localized_path = mkstemp(suffix=suffix)
        with open(localized_path, 'wb') as tmpfile:
            s3.download_fileobj(bucket, key, tmpfile)
            
    return localized_path


def delocalize(file, s3path):
    """
    uploads a file to s3
    """
    s3 = boto3.client('s3')

    bucket, *key = s3path.replace('s3://', '').split('/')
    key = '/'.join(key + [os.path.basename(file)])

    with open(file, 'rb') as data:
        s3.upload_fileobj(data, bucket, key)
    
    return 's3://' + '/'.join([bucket, key])


def get_variants(vcf_file, sample_method=None, sample_n=None, sample_seed=None):
    callset = allel.read_vcf(vcf_file)

    gt = allel.GenotypeArray(callset['calldata/GT'])

    # convert genotypes to numeric values
    gt_coded = gt.to_packed()
    gt_coded[gt_coded == 16] = 1
    gt_coded[gt_coded == 17] = 2

    features = [
        '{}-{}-{}-{}'.format(c, p, r, a[0])
        for c, p, r, a in zip(
            callset['variants/CHROM'], 
            callset['variants/POS'], 
            callset['variants/REF'], 
            callset['variants/ALT']
    )]
    features = np.array(features)

    data = pd.concat((
        pd.Series(features, name='features'),
        pd.DataFrame(gt_coded, columns=callset['samples'])
    ), axis=1)

    if sample_method and sample_n:
        if sample_n > data.shape[0]:
            sample_n = data.shape[0]

        if sample_method.lower() == 'first':
            data = data.head(sample_n).copy()

        elif sample_method.lower() == 'last':
            data = data.tail(sample_n).copy()

        elif sample_method.lower() == 'random':
            if sample_n < data.shape[0]:
                data = data.sample(sample_n, random_state=sample_seed).copy()
            
        else:
            raise RuntimeError("Unsupported sampling method")

    return data

def main(args):
    vcf_file = localize(args.vcf_file)
    
    data = get_variants(
        vcf_file,
        sample_method=args.sample_method,
        sample_n=args.sample_n,
        sample_seed=args.sample_seed
    )

    sampling = 'all'
    if args.sample_method:
        sampling = ''.join([args.sample_method, str(args.sample_n)])
    
    csv_file = re.sub('\.vcf.*$', '', os.path.basename(args.vcf_file), flags=re.I)
    csv_file = '.'.join([csv_file, sampling, 'csv'])

    data.to_csv(csv_file, index=False)

    if args.s3_output_path:
        delocalize(csv_file, args.s3_output_path)

    os.remove(vcf_file)
    os.remove(csv_file)

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
