# Testing constants
_test_s3_bucket_list = {'Buckets': [
    {'Name': 'OTA_test_S3_bucket'}, {'Name': 'OTA_test_S3_bucket2'}]}
_expected_json_status_code_response = {
    'ResponseMetadata': {
        'HTTPStatusCode': 200
    }
}
_error_json_status_code_response = {
    'ResponseMetadata': {
        'HTTPStatusCode': 400
    }
}
_test_s3_bucket_name = "OTA_test_S3_bucket"
_test_s3_file_upload_name = "OTA_test_S3_file_upload"
_expected_put_s3_object_response = {
    'ResponseMetadata': {
        'HTTPStatusCode': 200
    },
    'VersionId': 'test_version_id'
}
_test_iot_thing_list = {'things': [{'thingName': 'test_IoT_thing'}]}
_test_iot_thing_group_list = {'thingGroups': [
    {'groupName': 'test_IoT_thing_group'}]}
_test_iot_thing_name = "test_IoT_thing"
_test_create_iot_thing_response = {
    'ResponseMetadata': {
        'HTTPStatusCode': 200
    },
    'thingArn': {
        'test_IoT_thing'
    }
}
_test_create_iot_thing_group_response = {
    'ResponseMetadata': {
        'HTTPStatusCode': 200
    },
    'thingGroupArn': {
        'test_IoT_thing_group'
    }
}
_test_iot_thing_group_name = "test_IoT_thing_group_name"
_test_iot_thing_group_arn = "test_IoT_thing_group_arn"
_test_iot_thing_arn = "test_IoT_thing_group"
_test_iam_role_name = "test_iam_role"
_test_create_iam_role_response = {
    'ResponseMetadata': {
        'HTTPStatusCode': 200
    },
    'Role': {
        'Arn': 'test_iam_role_arn'
    }
}
_test_create_iam_role_response_error = {
    'ResponseMetadata': {
        'HTTPStatusCode': 400
    },
    'Role': {
        'Arn': 'test_iam_role_arn'
    }
}
_test_iam_role_list = {'Roles': [{'RoleName': 'test_iam_role'}]}
_test_import_acm_certificate_response = {
    'ResponseMetadata': {
        'HTTPStatusCode': 200
    },
    'CertificateArn': {
        'test_acm_certificate'
    }
}
_test_acm_certificate_arn = "test_acm_certificate_arn"
_test_acm_certificate_private_key = "test_acm_private_key"
_test_acm_certificate_list = {'CertificateSummaryList': [
    {'CertificateArn': 'test_acm_certificate'}]}
_test_codesigner_profile_name = "test_codesigner"
_test_codesigner_profile_list = {
    'profiles': [{'profileName': 'test_codesigner'}]}
