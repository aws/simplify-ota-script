  # AWS-Simplify-OTA-Script
This repository provides a command line interface wizard for easily onboarding IoT things to AWS IoT core, thing group management, and OTA job creation.
This library is distributed under the [Apache-2.0 Open Source License](https://github.com/aws/simplify-ota-script/blob/main/LICENSE).

### Overview

This package currently has 4 source files:
* `aws_operations.py` is a wrapper for each AWS SDK call
* `utils.py` helps handle input and output
* `setup_ota_update.py` runs infrastructure setup for the user. This is the entry point of the script.
	* When resources are created or configured, the configuration gets written to `config.json`. 
* `run_ota_update.py` is a wrapper for CreateOTAUpdate API and reads from `config.json` to get the input needed for it.

### Prerequisites

#### [Install Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)

#### Create AWS Account
Follow the instructions [here](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/) to create an AWS account.

#### Setup AWS CLI
Follow the instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) to set up AWS CLI.

### Getting started
This [ documentation page](https://freertos.org/ota/ota-mqtt-agent-demo.html)  describes how to run an Over-the-Air (OTA) update agent as one of the RTOS tasks that share the same MQTT connection.

### Steps to run the script
To run this tool, you must first configure your AWS credentials. To see how to do this, refer to the following [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html). For example, in the terminal, run this with your configured credentials:

```
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_DEFAULT_REGION=us-west-2
```

After configuring your CLI credentials in your preferred method, simply run the following:

`python3 setup-ota-update.py`

This will take you through setting up the infrastructure for an OTA update. You will be prompted if you want to create a new resource or use an existing one for each needed resource, such as IAM roles, S3 buckets, Code signing profiles, etc.

If you generate an OpenSSL certificate through the wizard, you will have two files in your directory, `ecdsasigner-priv-key.pem` and `ecdsasigner.crt`. You should make sure that your device is signed with the private key file, or else the OTA update will not succeed.

When you are ready, simply run 

`python3 run-ota-update.py`

Which will create the OTA update. You should go into your account or use the CLI to view the status of the update.
