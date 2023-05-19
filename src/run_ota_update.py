""" Wrapper to call CreateOTAUpdate from the AWS SDK"""
import json
import boto3

def create_ota_update():
    """ Creates an OTA update using the data from config.json """

    with open('config.json', 'r', encoding="utf-8") as config_file:
        data = json.load(config_file)

    aws_iot_client = boto3.client('iot')

    response = aws_iot_client.create_ota_update(
        otaUpdateId=data['otaUpdateId'],
        targetSelection=data['targetSelection'],
        files=data['files'],
        targets=data['targets'],
        roleArn=data['roleArn'],
    )

    # TODO: Wait for the status, some sort of animation?
    print(response)
    return response['ResponseMetadata']['HTTPStatusCode'] == 200

if __name__ == '__main__':
    create_ota_update()
