#!/usr/bin/env python
# for any issues please email cmsc@gmx.com

import sys
import os
import argparse
import logging
import json
import boto3
from botocore.exceptions import ClientError
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

"""
module: aws_iam_account_alias
short_description: "Ensure the compliance of AWS alias name"
author:
  - chander
requirements:
  - import os, sys, argparse, json, boto3 library needed
options:
  aws_account_alias:
    description:
      - the name of the account alias you want to create or update
      required: true
      default: null

  aws_account_state:
    description:
      - the state of the account alias
      required: present/absent
      default: present

  aws_access_key_id:
    description:
      - the name of the aws access key id
      required: false
      default: null

  aws_access_key:
    description:
      - the name of the aws access key
      required: false
      default: null

example:  aws_iam_account_alias: aws_account_alias="newnametest"
                                 aws_account_state=present
                                 aws_access_key_id="23sdf"
                                 aws_access_key="wqerf332sdfasdfsa"
"""



# Function to create the account alias

def create_aws_account_alias(awsaccount_alias):
    """
    Function create_aws_account_alias
      description :
        - It  will accept the name of aws account alias name and change it. It will not change
      required : The aws account alias
      default  : null
    """
    try:
        response = CLIENT.create_account_alias(AccountAlias=awsaccount_alias)
        return response
    except ClientError as err:
        if err.response['Error']['Code'] == 'EntityAlreadyExists':
            response = "EntityAlreadyExists"
            return response
        else:
            response = "Unexpected error"
            return response

# Function to return the status in json format

def aws_account_status_result(client_id, awsaccount_alias, changed):
    """
    Function aws_account_status_result
      description :
        - It  will create json output for result.
      required : Client id , aws account alias  and true/false value
      default  : null
    """

    status = {
        "changed": changed,
        "aws_account_id": client_id,
        "aws_account_alias": awsaccount_alias
    }
    # creating json dump
    jsondata = json.dumps(status)
    return jsondata


# Function to delete the account alias

def delete_aws_account_alias(awsaccount_alias):
    """
    Function delete_aws_account_alias
      description :
        - It will accept the name of aws account alias name and and delete it.
        - It Will also return success and error message.
      required : The aws account alias
      default  : null
    """
    try:
        response = CLIENT.delete_account_alias(AccountAlias=awsaccount_alias)
        return response
    except ClientError as err:
        if err.response['Error']['Code'] == 'NoSuchEntity':
            response = "NoSuchEntity"
            return response
        else:
            response = "Unexpected error"
            return response


# Accept arguments to the script

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--aws_account_alias",
                    help="AWS account alias name,If not set, the script will do nothing")
PARSER.add_argument("--aws_account_state",
                    default='present',
                    help="AWS account state.If 'absent' then delete,if set to 'present' then create/update")
PARSER.add_argument("--aws_access_key_id",
                    help="if not set, then the value of AWS_ACCESS_KEY_ID environment variable will be used")
PARSER.add_argument("--aws_secret_key",
                    help="if not set,then the value of AWS_SECRET_ACCESS_KEY environment variable will be used")

# Argument parsing

ARGS = PARSER.parse_args()

AWSACCOUNT_ALIAS = ARGS.aws_account_alias


# Set the aws_access_key_id environment value from --aw_access_key_id parameter

if ARGS.aws_access_key_id:
    os.environ["AWS_ACCESS_KEY_ID"] = ARGS.aws_access_key_id

# Set the aws_secret_access_key environment value from --aws_secret_value parameter

if ARGS.aws_secret_key:
    os.environ["AWS_SECRET_ACCESS_KEY"] = ARGS.aws_secret_access_key

# proceed only if aws_account_alias is set otherwise comeout

if ARGS.aws_account_alias:

    # Calling boto library's iam call

    CLIENT = boto3.client('iam')
    # calling boto library's sts call to get the caller_identity
    CLIENT_ID = boto3.client('sts').get_caller_identity().get('Account')
    if ARGS.aws_account_state == 'present':
        AWS_ALIAS_RESPONSE = create_aws_account_alias(AWSACCOUNT_ALIAS)
        # Checking Response from Boto library
        if AWS_ALIAS_RESPONSE == 'EntityAlreadyExists' or AWS_ALIAS_RESPONSE == 'Unexpected error':
            CHANGED = 'False'
        else:
            CHANGED = 'True'
        JSON_RETURN = aws_account_status_result(CLIENT_ID, ARGS.aws_account_alias, CHANGED)
        print JSON_RETURN

    elif ARGS.aws_account_state == 'absent':
        DELETE_AWS_ALIAS_RESPONSE = delete_aws_account_alias(AWSACCOUNT_ALIAS)
        # Checking response from boto library
        if DELETE_AWS_ALIAS_RESPONSE == 'NoSuchEntity' or DELETE_AWS_ALIAS_RESPONSE == 'Unexpected error':
            CHANGED = 'False'
        else:
            CHANGED = 'True'

        JSON_RETURN = aws_account_status_result(CLIENT_ID, ARGS.aws_account_alias, CHANGED)
        print JSON_RETURN
    else:
        print ("aws account state can be only present or absent")
else:
    print(os.path.basename(sys.argv[0]) + "  -h")
