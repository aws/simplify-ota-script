import constants
from botocore.exceptions import ClientError
import unittest
import unittest.mock as mock
from unittest.mock import patch, MagicMock
import sys
sys.path.append("/Volumes/workplace/FreeRTOSSimplifyOTAWorkflow/src/FreeRTOSSimplifyOTAWorkflow/simplify_ota/src")
from aws_operations import AwsOperations

class aws_operations_test(unittest.TestCase):

    def test_list_s3_buckets_with_valid_bucket_list(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_s3_bucket_list
            boto3_client_mock.list_buckets.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.list_s3_buckets()
            assert actual_response == mock_response['Buckets']

    def test_create_s3_bucket_with_valid_name(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._expected_json_status_code_response
            boto3_client_mock.create_bucket.return_value = mock_response
            boto3_client_mock.put_bucket_versioning.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.create_s3_bucket(
                constants._test_s3_bucket_name)
            assert actual_response == (
                mock_response['ResponseMetadata']['HTTPStatusCode'] == 200)

    def test_create_s3_bucket_with_existing_name(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._error_json_status_code_response
            boto3_client_mock.create_bucket.return_value = mock_response
            boto3_client_mock.put_bucket_versioning.return_value = mock_response
            aws_proxy = AwsOperations()
            with self.assertRaises(SystemExit):
                actual_response = aws_proxy.create_s3_bucket(
                    constants._test_s3_bucket_name)
                assert actual_response == (
                    mock_response['ResponseMetadata']['HTTPStatusCode'] == 400)

    def test_put_s3_object_with_valid_object(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            with patch('builtins.open', mock.mock_open(read_data='test_data')):
                mock_response = constants._expected_put_s3_object_response
                boto3_client_mock.put_object.return_value = mock_response
                aws_proxy = AwsOperations()
                actual_response = aws_proxy.put_s3_object(
                    constants._test_s3_file_upload_name
                )
                assert actual_response == (
                    mock_response['ResponseMetadata']['HTTPStatusCode'] == 200)

    def test_list_iot_things_with_valid_thing_list(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_iot_thing_list
            boto3_client_mock.list_things.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.list_iot_things()
            assert actual_response == mock_response['things']

    def test_list_iot_things_groups_with_valid_thing_group_list(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_iot_thing_group_list
            boto3_client_mock.list_thing_groups.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.list_iot_thing_groups()
            assert actual_response == mock_response['thingGroups']

    def test_create_iot_thing_with_valid_thing_name(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_create_iot_thing_response
            boto3_client_mock.create_thing.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.create_iot_thing(
                constants._test_iot_thing_name)
            assert actual_response == (
                mock_response['ResponseMetadata']['HTTPStatusCode'] == 200)

    def test_create_iot_thing_group_with_valid_thing_group_name(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_create_iot_thing_group_response
            boto3_client_mock.create_thing_group.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.create_iot_thing_group(
                constants._test_iot_thing_group_name)
            assert (actual_response['ResponseMetadata']['HTTPStatusCode'] == 200) == (
                mock_response['ResponseMetadata']['HTTPStatusCode'] == 200)

    def test_add_thing_to_thing_group_with_valid_thing_name(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._expected_json_status_code_response
            boto3_client_mock.add_thing_to_thing_group.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.add_thing_to_thing_group(
                constants._test_iot_thing_group_name,
                constants._test_iot_thing_group_arn,
                constants._test_iot_thing_name,
                constants._test_iot_thing_arn
            )
            assert actual_response == (
                mock_response['ResponseMetadata']['HTTPStatusCode'] == 200)

    def test_list_iam_roles_with_valid_iam_role_list(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_iam_role_list
            boto3_client_mock.list_roles.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.list_iam_roles()
            assert actual_response == mock_response['Roles']

    def test_create_iam_role_with_new_role_name(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_create_iam_role_response
            boto3_client_mock.create_role.return_value = mock_response
            boto3_client_mock.attach_role_policy.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.create_iam_role(
                constants._test_iam_role_name)
            assert actual_response == (
                mock_response['ResponseMetadata']['HTTPStatusCode'] == 200)

    def test_create_iam_role_with_existing_role_name(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_create_iam_role_response
            boto3_client_mock.create_role.side_effect = ClientError(
                {'Error': {'Code': 'EntityAlreadyExists'}}, 'create_role')
            boto3_client_mock.get_role.return_value = mock_response
            boto3_client_mock.attach_role_policy.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.create_iam_role(
                constants._test_iam_role_name)
            assert actual_response == (
                mock_response['ResponseMetadata']['HTTPStatusCode'] == 200)

    def test_create_iam_role_with_unexpected_response(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_create_iam_role_response_error
            boto3_client_mock.create_role.return_value = mock_response
            aws_proxy = AwsOperations()
            with self.assertRaises(SystemExit):
                actual_response = aws_proxy.create_iam_role(
                    constants._test_iam_role_name)

    def test_import_acm_certificate_with_valid_certificate_and_private_key(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_import_acm_certificate_response
            boto3_client_mock.import_certificate.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.import_acm_certificate(
                constants._test_acm_certificate_arn, constants._test_acm_certificate_private_key)
            assert actual_response == (
                mock_response['ResponseMetadata']['HTTPStatusCode'] == 200)

    def test_list_acm_certs_with_valid_certificate_list(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_acm_certificate_list
            boto3_client_mock.list_certificates.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.list_acm_certs()
            assert actual_response == mock_response['CertificateSummaryList']

    def test_put_signing_profile_with_valid_profile_name(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._expected_json_status_code_response
            boto3_client_mock.put_signing_profile.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.put_signing_profile(
                constants._test_codesigner_profile_name)
            assert actual_response == (
                mock_response['ResponseMetadata']['HTTPStatusCode'] == 200)

    def test_list_signing_profiles_with_valid_profile_list(self):
        boto3_client_mock = mock.Mock()
        with mock.patch('boto3.client', return_value=boto3_client_mock):
            mock_response = constants._test_codesigner_profile_list
            boto3_client_mock.list_signing_profiles.return_value = mock_response
            aws_proxy = AwsOperations()
            actual_response = aws_proxy.list_signing_profiles()
            assert actual_response == mock_response['profiles']

    if __name__ == '__main__':
        unittest.main()
