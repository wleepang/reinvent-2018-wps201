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


def get_variants(vcf_file, s3_output_path=None, freq_thresh=.30):
    vcf_path = localize(vcf_file)
    callset = allel.read_vcf(vcf_path)

    REF = callset['variants/REF']
    ALT = callset['variants/ALT']

    gt = allel.GenotypeArray(callset['calldata/GT'])

    # looking for only bi-allelic SNPs, so we're only concerned with 
    # single base references and variants with only one alternative
    is_1bp_ref = np.array(list(map(lambda r: len(r) == 1, REF)), dtype=bool)
    is_1bp_alt = np.array(list(map(lambda a: len(a[0]) == 1 and not any(a[1:]), ALT)), dtype=bool)
    is_snp_var = is_1bp_ref & is_1bp_alt

    # reduce to high frequency alleles
    ac = gt.count_alleles()
    is_hifreq_snp_var = is_snp_var & (ac[:, 1] / (ac[:, 0] + ac[:, 1]) > freq_thresh)

    # convert genotypes to numeric values
    gt_coded = gt.to_packed()[is_hifreq_snp_var,:]
    gt_coded[gt_coded == 16] = 1
    gt_coded[gt_coded == 17] = 2
    gt_coded.transpose()

    features = [
        '{}-{}-{}-{}'.format(c, p, r, a[0])
        for c, p, r, a in zip(
            callset['variants/CHROM'], 
            callset['variants/POS'], 
            callset['variants/REF'], 
            callset['variants/ALT']
    )]
    features = np.array(features)[is_hifreq_snp_var]

    # remove source data file to save space
    os.remove(vcf_path)

    data = pd.concat((
        pd.Series(callset['samples'], name='sample'),
        pd.DataFrame(gt_coded.transpose(), columns=features)
    ), axis=1)

    csv_file = re.sub('\.vcf.*$', '.csv', os.path.basename(vcf_file), flags=re.I)
    data.to_csv(csv_file)

    if s3_output_path:
        delocalize(csv_file, s3_output_path)

    return {
        'data': {
            'vals': gt_coded.transpose(),
            'rows': callset['samples'], 
            'cols': features
        },
        'call' : {
            'function': 'get_variants',
            'args': {
                'vcf_file': vcf_file,
                'freq_thresh': freq_thresh
            }
        }
    }

def main(args):
    get_variants(args.vcf_file, s3_output_path=args.s3_output_path)

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
