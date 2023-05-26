""" This file serves as a wrapper for AWS SDK calls """
import json
import sys
import boto3
from botocore.exceptions import ClientError

# The minimal assume role policy for IoT
iotAssumeRolePolicy = json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "iot.amazonaws.com"
                ]
            },
            "Action": [
                "sts:AssumeRole"
            ]
        }
    ]
})


class AwsOperations:
    """ A Wrapper for AWS SDK calls and storage of their object data """

    def __init__(self):

        # Initialize all of the AWS Clients
        self._aws_iot_client = boto3.client('iot')
        self._aws_s3_client = boto3.client('s3')
        self._aws_iam_client = boto3.client('iam')
        self._aws_acm_client = boto3.client('acm')
        self._aws_signer_client = boto3.client('signer')
        self._aws_sts_client = boto3.client('sts')

        # Every object we need to execute the OTA update
        # These will be stored here and then moved to config.json
        self.s3_bucket = ""
        self.s3_object_key = ""
        self.s3_object_version = ""
        self.ota_role_arn = ""
        self.thing_arn = ""
        self.thing_group_arn = ""
        self.cert_arn = ""
        self.target_selection = ""
        self.signing_profile_name = ""

        self.account_id = self._aws_sts_client.get_caller_identity()['Account']

    def list_s3_buckets(self):
        """Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_buckets.html """
        return self._aws_s3_client.list_buckets()['Buckets']

    def create_s3_bucket(self, bucket_name):
        """Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html """

        # Create a bucket with private permissions and the inputted bucket name
        create_bucket_response = self._aws_s3_client.create_bucket(
            ACL='private',
            Bucket=bucket_name,
        )

        # If the call failed, error out
        # TODO: how to show this to the user
        if create_bucket_response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print(create_bucket_response)
            sys.exit()

        # Enable versioning (needed for OTA)
        response = self._aws_s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={
                'Status': 'Enabled'
            }
        )

        self.s3_bucket = bucket_name

        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    def put_s3_object(self, file_name):
        """Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/bucket/put_object.html#put-object """

        # Open the file and put it into the bucket with the filename as a key
        with open(file_name, 'rb') as object_file:
            response = self._aws_s3_client.put_object(
                Body=object_file,
                Bucket=self.s3_bucket,
                Key=file_name
            )

        self.s3_object_key = file_name

        self.s3_object_version = response['VersionId']

        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    def list_iot_things(self):
        """ Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot/client/list_things.html#list-things """
        return self._aws_iot_client.list_things()['things']

    def list_iot_thing_groups(self):
        """ Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot/client/list_thing_groups.html#list-thing-groups """
        return self._aws_iot_client.list_thing_groups()['thingGroups']

    def create_iot_thing(self, thing_name):
        """ Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot/client/create_thing.html#create-thing """
        response = self._aws_iot_client.create_thing(
            thingName=thing_name
        )

        self.thing_arn = response['thingArn']

        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    def create_iot_thing_group(self, thing_group_name):
        """ Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot/client/create_thing_group.html#create-thing-group """
        response = self._aws_iot_client.create_thing_group(
            thingGroupName=thing_group_name
        )

        self.thing_group_arn = response['thingGroupArn']

        return response

    def add_thing_to_thing_group(self, thing_group_name, thing_group_arn, thing_name, thing_arn):
        """ Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot/client/add_thing_to_thing_group.html#add-thing-to-thing-group """
        response = self._aws_iot_client.add_thing_to_thing_group(
            thingGroupName=thing_group_name,
            thingGroupArn=thing_group_arn,
            thingName=thing_name,
            thingArn=thing_arn
        )

        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    def list_iam_roles(self):
        """ Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam/client/list_roles.html#list-roles """
        return self._aws_iam_client.list_roles()['Roles']

    def create_json_policy(self, account_id, role_name):
        """ Helper method that creates a JSON policy for use in initial IAM role setup """
        iam_policy = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "iam:GetRole",
                        "iam:PassRole"
                    ],
                    "Resource": f"arn:aws:iam::{account_id}:role/{role_name}"
                }
            ]
        })
        return iam_policy

    def create_iam_role(self, role_name):
        """ Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam/client/create_role.html#create-role """

        # Create a role that can assume IoT
        try:
            response = self._aws_iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=iotAssumeRolePolicy
            )
            self.ota_role_arn = response['Role']['Arn']

        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print("Role already exists. We can use that instead")

                response = self._aws_iam_client.get_role(
                    RoleName=role_name,
                )
                self.ota_role_arn = response['Role']['Arn']

        # If the call failed, error out
        # TODO: how to show this to the user
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print(response)
            sys.exit()

        # Attach the managed policy AmazonFreeRTOSOTAUpdate to the role
        response = self._aws_iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonFreeRTOSOTAUpdate'
        )
        # Attach the inline policy created to the role
        response = self._aws_iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName='OTAPolicy',
            PolicyDocument=self.create_json_policy(self.account_id, role_name)
        )

        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    def import_acm_certificate(self, certificate, privatekey):
        """ Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/acm/client/import_certificate.html#import-certificate """
        # Import a certificate to the account with cert and pkey generated from openssl
        response = self._aws_acm_client.import_certificate(
            Certificate=certificate,
            PrivateKey=privatekey
        )
        self.cert_arn = response['CertificateArn']

        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    def list_acm_certs(self):
        """ Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/acm/client/list_certificates.html#list-certificates """
        # NOTE: need to include all key types here, otherwise will only return RSA_1024 by default
        response = self._aws_acm_client.list_certificates(
            Includes={
                'keyTypes': ['EC_prime256v1', 'RSA_1024', 'RSA_2048']
            }
        )
        return response['CertificateSummaryList']

    def put_signing_profile(self, input_profile_name):
        """ Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/signer/client/put_signing_profile.html#put-signing-profile """
        # Signer takes in a certificate and creates a profile out of it
        response = self._aws_signer_client.put_signing_profile(
            profileName=input_profile_name,
            signingMaterial={
                'certificateArn': self.cert_arn
            },
            platformId="AmazonFreeRTOS-Default",
            signingParameters={
                'certname': "ecdsasigner.crt"
            }
        )

        self.signing_profile_name = input_profile_name

        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    def list_signing_profiles(self):
        """ Wrapper for https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/signer/client/list_signing_profiles.html#list-signing-profiles """
        return self._aws_signer_client.list_signing_profiles()['profiles']