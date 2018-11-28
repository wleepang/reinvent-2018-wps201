# Builder Session - WPS201

![WPS201 - Genome Clustering with SageMaker](images/banner-image.png)

## Session Description

The development and application of machine learning (ML) models is a vital part of scientific and technical computing. Increasing model training data size generally improves model prediction and performance, but deploying models at scale is a challenge. Participants in this builder session learn to use Amazon SageMaker, an AWS service that simplifies the ML process and enables training on cloud-stored datasets at any scale. Attendees walk through the process of building a model, training it, and applying it for prediction against large open scientific datasets, such as the 1000 Genomes data. By the end of the session, attendees have the resources and experience to start using Amazon SageMaker and related AWS services to accelerate their scientific research and time to discovery.

## Prerequisites

Attendees are encouraged to have the following:

* Administrative access to an AWS Account
* Familiarity with the [Python](https://python.org) programming language
* Familiarity with [Jupyter](https://jupyter.org) [Notebooks](https://jupyter-notebook.readthedocs.io/en/stable/)

## Getting started

### Applying credits to your account

Credits have been provided to you so that you can participate hands-on during
the session at no cost!

1. Sign-in to the [AWS Console](http://console.aws.amazon.com/)
2. Go to the Billing Console

    ![billing-console](images/search-billing-console.png)

3. Click on "Credits" in the list on the left

    ![billing-credits](images/billing-credits-ui.png)

4. Enter your credit code in the "Promo Code" box
5. Enter the Security check text
6. Click on the "Redeem" button

### Create resources with CloudFormation

For this session, we'll use CloudFormation to create the following infrastructure

![session infrastructure](images/cfn-infrastructure.png)

!!! warning
    The CloudFormation templates used will create IAM roles.  In order for the
    stack to be successfully created you **must** have Administrative access to
    the AWS Account used.

<a class="btn btn-warning btn-block" target="_blank"
    href="https://console.aws.amazon.com/cloudformation/home?#/stacks/new?region=us-west-2&stackName=wps201&templateURL=https://s3.amazonaws.com/reinvent-2018-wps201/templates/wps201-root-novpc.template.yaml">
    Launch Stack
</a>

Clicking the button above will take you to a CloudFormation Console.
When the console opens, do the following:

1. On the "Select Template" page, click the "Next" button
2. On the "Specify Details" page:

    1. Use the pre-populated stack name ("wps201")

    2. Select a VPC.  This will be where EC2 instances created by AWS Batch will be launched.
       If you have multiple VPCs you can either use your default one (the CIDR block starts with 172),
       or one that already exists in your account.

        ![select vpc](images/cfn-select-vpc.png)

    3. Select at least one subnet id.  This should be in the VPC you selected.
       Again, you can tell by the CIDR block which VPC a subnet is in.

        ![select subnets](images/cfn-select-subnets.png)

    4. (Optional) Specify the Spot bid percentage relative to On-Demand pricing.
       This is the maximum bid price for a Spot instance AWS Batch will use.
       Batch will not launch an instance if spot instance pricing goes above this value.

3. Click "Next" through the "Options" page:

4. On the "Review" page be sure to check the boxes acknowledging IAM resource creation and 
   the requirement for CAPBILITY_AUTO_EXPAND

    ![acknowledge capabilities](images/cfn-acknowledge-capabilities.png)

5. Click the "Create" button

Stack creation should take about 5-10min to complete.  If successful, your CloudFormation
will look like the following:

![stack creation](images/cfn-stack-creation.png)

### Open your SageMaker notebook instance

1. Go to the Amazon SageMaker Console
   ![goto sagemaker](images/search-sagemaker-console.png)

2. Go to "Notebook Instances".  The instance for this session should be listed.
   Click on the "Open Jupyter" link next to the instance.
   ![open jupyter](images/sagemaker-console-ui.png)

3. Open the Jupyter Notebook `wps201-* / genome-kmeans-py3.ipynb`:
   ![open notebook 1](images/notebook-instance-1.png)
   ![open notebook 2](images/notebook-instance-2.png)

## Run the lab

The lab for this session is contained with in the Jupyter Notebook you opened above.
Detailed instructions are provided to guide you through building and deploying
a clustering model with SageMaker.

## Clean-up

To ensure that you are not charged for resources you are not using, it is recommended
that you run the following steps below when the session is complete.

### Remove Sagemaker Endpoints

1. Go to the Amazon SageMaker Console

2. Go to "Endpoints".  Endpoints you deployed for this session should be listed
   as `kmeans-YYYY-MM-DD-HH-mm-SS-XXXXXX`

3. Select an endpoint by clicking the radio button next to it.

4. From the "Actions" drop-down select "Delete"

![delete endpoint](images/sagemaker-delete-endpoint.png)

### Delete CloudFormation Stacks

Deleting the CloudFormation stack you created in the [Getting Started](#getting-started)
section will remove the SageMaker Notebook instance and AWS Batch resources (Job Queue
and Compute Environment).  The S3 Bucket created needs to be removed manually
(see below).

!!! note
    You are only charged for actively running instances.  If you would like to
    keep your notebook instance for later use, you can simply "Stop" it from
    the Amazon SageMaker Console to avoid charges.  Similarly, for AWS Batch
    your account is only charged when you have actively running jobs.

1. Go to the CloudFormation Console

2. Select the **root** stack for this session (it is the one that does **not** have
   "NESTED" next to its name)

3. Select "Delete Stack" from the Actions drop-down.
   ![delete stack 1](images/cfn-delete-stack-1.png)

4. Confirm the deletion in the subsequent dialog.
   ![delete stack 2](images/cfn-delete-stack-2.png)

### Delete S3 Bucket

The S3 bucket created for this session will contain processed data and trained
model artifacts.

1. Go to the S3 Console

2. Select the bucket that was created by CloudFormation

3. Click on the "Delete" button

![delete s3 bucket](images/s3-delete-bucket.png)
