""" This file builds infrastructure for an OTA update """
import os
import json
import sys
from string import Template
from aws_operations import AwsOperations
import run_ota_update
import utils

CERT_FILE = "selfsigned.crt"
KEY_FILE = "private.key"


def cert_gen(aws_proxy, email_address="emailAddress"):
    """ Generates a certificate and imports it to aws """
    email = {'email': email_address}
    with open("cert_template.txt", "r", encoding="utf-8") as cert_template:
        src = Template(cert_template.read())
        result = src.substitute(email)
    with open("cert_config.txt", "w", encoding="utf-8") as cert_config:
        cert_config.write(result)

    os.system("openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 \
               -pkeyopt ec_param_enc:named_curve -outform PEM -out ecdsasigner-priv-key.pem")
    os.system("openssl req -new -x509 -config cert_config.txt -extensions my_exts \
               -nodes -days 365 -key ecdsasigner-priv-key.pem -out ecdsasigner.crt")

    with open("ecdsasigner.crt", "r", encoding="utf-8") as cert_file:
        cert = cert_file.read()
        cert_file.close()
    with open("ecdsasigner-priv-key.pem", "r", encoding="utf-8") as pkey_file:
        pkey = pkey_file.read()
        pkey_file.close()
    return aws_proxy.import_acm_certificate(cert, pkey)


def setup_ota_update():
    """ Creates infra to execute an OTA update """
    print("Welcome to the OTA CLI script \nPlease select an S3 bucket option to host your ota updates")
    aws_proxy = AwsOperations()

    # Create or select an S3 bucket
    new_bucket = "Create a new S3 Bucket"
    old_bucket = "Use an existing S3 Bucket"
    choice = utils.handle_input_a_or_b(new_bucket, old_bucket)

    if choice == new_bucket:
        print("Enter an S3 bucket name (S3 bucket names can consist only of lowercase letters, numbers, dots (.), and hyphens (-))")
        new_s3_bucket_name = input()

        if aws_proxy.create_s3_bucket(new_s3_bucket_name):
            print("Successfully created a new bucket")
        else:
            print("Something went wrong while creating a new bucket of name %s",
                  new_s3_bucket_name)
            sys.exit()
    else:
        s3_buckets = utils.PaginationOnKey(aws_proxy.list_s3_buckets(), 'Name')

        selected_bucket = s3_buckets.handle_pagination()

        print(f"You selected {selected_bucket['Name']}\n")

        aws_proxy.s3_bucket = selected_bucket['Name']

    # Create or select a thing/thing group
    use_thing = "Create or use an IoT thing."
    use_thing_group = "Create or use an Iot thing group."
    choice = utils.handle_input_a_or_b(use_thing, use_thing_group)
    # Create or use a thing
    if choice == use_thing:
        print("Select a thing option")
        new_thing = "Create a new IoT thing."
        existing_thing = "Use an existing IoT thing."
        choice = utils.handle_input_a_or_b(new_thing, existing_thing)
        if choice == new_thing:
            print(
                "Enter a new thing name, or leave blank to create a thing named \"MyOTAThing\"")
            new_thing_name = input()
            new_thing_name = new_thing_name if new_thing_name != "" else "MyOTAThing"

            if aws_proxy.create_iot_thing(new_thing_name):
                print(
                    f"Successfully created a new thing named {new_thing_name}")
            else:
                print("Something went wrong while creating a new thing")
                sys.exit()
        else:
            print("Choose an IoT thing")
            iot_things = utils.PaginationOnKey(
                aws_proxy.list_iot_things(), 'thingName')

            selected_thing = iot_things.handle_pagination()

            print(f"You selected {selected_thing['thingName']}\n")

            aws_proxy.thing_arn = selected_thing['thingArn']

    # Create or use a thing group
    else:
        print("Select a thing group option")
        new_thing_group = "Create a new Iot thing group."
        existing_thing_group = "use an existing IoT thing group."
        choice = utils.handle_input_a_or_b(
            new_thing_group, existing_thing_group)
        if choice == new_thing_group:
            print(
                "Enter a new thing group name, or leave blank to create a thing group named \"MyOTAThingGroup\"")
            new_thing_group_name = input()
            new_thing_group_name = new_thing_group_name if new_thing_group_name != "" else "MyOTAThingGroup"
            response = aws_proxy.create_iot_thing_group(new_thing_group_name)
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print(
                    f"Successfully created a new thing named {new_thing_group_name}")
                user_has_things_to_add = True
                while(user_has_things_to_add):
                    print("Select a thing to add to the thing group")
                    iot_things = utils.PaginationOnKey(
                        aws_proxy.list_iot_things(), 'thingName')

                    selected_thing = iot_things.handle_pagination()

                    print(f"You selected {selected_thing['thingName']}\n")

                    aws_proxy.thing_group_arn = response['thingGroupArn']
                    aws_proxy.thing_name = selected_thing['thingName']
                    aws_proxy.thing_arn = selected_thing['thingArn']
                    aws_proxy.add_thing_to_thing_group(new_thing_group_name, aws_proxy.thing_group_arn, aws_proxy.thing_name, aws_proxy.thing_arn)
                    print("Do you want to add another thing to the thing group?")
                    choice = utils.handle_y_n()
                    if not choice:
                        user_has_things_to_add = False

                
            else:
                print("Something went wrong while creating a new thing group.")
                sys.exit()
        else:
            print("Choose an IoT thing group.")
            iot_thing_groups = utils.PaginationOnKey(
                aws_proxy.list_iot_thing_groups(), 'groupName')

            selected_thing = iot_thing_groups.handle_pagination()

            print(f"You selected {selected_thing['groupName']}\n")

            aws_proxy.thing_group_arn = selected_thing['groupArn']

    # Create or select a role, and it will attach the policies to it
    print("Create or use an IAM Role to deploy your OTA updates with.")
    new_role = "Create a new IAM Role"
    old_role = "Use an existing IAM Role"
    choice = utils.handle_input_a_or_b(new_role, old_role)

    if choice == new_role:
        print("A new role will be created with the required OTA permissions.")
        print("Enter a new role name, or leave blank to create a role named \"MyOTARole\"")
        new_role_name = input()

        new_role_name = new_role_name if new_role_name != "" else "MyOTARole"

        if aws_proxy.create_iam_role(new_role_name):
            print(f"Successfully created a new role named {new_role_name}")
        else:
            print("Something went wrong while creating a new role.")
            sys.exit()
    else:
        roles = utils.PaginationOnKey(aws_proxy.list_iam_roles(), 'RoleName')

        selected_role = roles.handle_pagination()

        print(f"You selected {selected_role['RoleName']}\n")

        aws_proxy.ota_role_arn = selected_role['Arn']

    # Create or select a signing profile
    new_signing_profile = "Create a new Signing Profile."
    old_signing_profile = "Use an existing Signing Profile."
    choice = utils.handle_input_a_or_b(
        new_signing_profile, old_signing_profile)

    # Only on new signing profile, create or select a cert
    if choice == new_signing_profile:

        new_cert = "Create a new ACM Certificate."
        old_cert = "Use an existing ACM Cerficiate."
        choice = utils.handle_input_a_or_b(new_cert, old_cert)

        if choice == new_cert:
            print("Enter an email to use for the certificate")
            input_email = input()

            if cert_gen(aws_proxy, input_email):
                print("Successfully created a new certificate")
            else:
                print("Something went wrong while creating a new certificate")
                sys.exit()
        else:
            acm_certs = utils.PaginationOnKey(
                aws_proxy.list_acm_certs(), 'CertificateArn')

            selected_cert = acm_certs.handle_pagination()

            print(f"You selected {selected_cert['CertificateArn']}\n")

            aws_proxy.cert_arn = selected_cert['CertificateArn']

        print("Enter a new signing profile name, or leave blank to create a profile named \"MyOTASigningProfile\"")
        input_profile_name = input()

        input_profile_name = input_profile_name if input_profile_name != "" else "MyOTASigningProfile"

        aws_proxy.put_signing_profile(input_profile_name)
    else:
        profiles = utils.PaginationOnKey(
            aws_proxy.list_signing_profiles(), 'profileName')

        selected_profile = profiles.handle_pagination()

        print(f"You selected {selected_profile['profileName']}\n")

        aws_proxy.signing_profile_name = selected_profile['profileName']

    # Upload a file to the S3 bucket
    print("Let's upload a file to the S3 bucket")

    print("Enter a filepath to use for the OTA update; if following a demo, this will be the \"demo_config.h\" file located in the respective demo's folder.")
    filepath = input()
    aws_proxy.put_s3_object(filepath)

    # Input Job Name
    print("What do you want your OTA job to be called? This must be unique to your account.")
    job_name = input()

    # Continuous or snapshot
    print("Do you want your OTA update to be continuous or snapshot?")
    continuous = "Continuous"
    snapshot = "Snapshot"
    choice = utils.handle_input_a_or_b(continuous, snapshot)

    aws_proxy.target_selection = "CONTINUOUS" if choice == continuous else "SNAPSHOT"

    # Open the config file and upload the data to it
    with open('config_template.json', 'r', encoding="utf-8") as config_template:
        data = json.load(config_template)

    # Write to the config file
    data['otaUpdateId'] = job_name
    data['roleArn'] = aws_proxy.ota_role_arn
    data['targets'] = []
    data['targets'].append(aws_proxy.thing_arn) if aws_proxy.thing_arn else data['targets'].append(aws_proxy.thing_group_arn)
    data['targetSelection'] = aws_proxy.target_selection
    data['files'][0]['fileLocation']['s3Location']['bucket'] = aws_proxy.s3_bucket
    data['files'][0]['fileLocation']['s3Location']['key'] = aws_proxy.s3_object_key
    data['files'][0]['fileLocation']['s3Location']['version'] = aws_proxy.s3_object_version

    data['files'][0]['codeSigning']['startSigningJobParameter']['destination']['s3Destination']['bucket'] = aws_proxy.s3_bucket
    data['files'][0]['codeSigning']['startSigningJobParameter']['signingProfileName'] = aws_proxy.signing_profile_name
    data['files'][0]['fileName'] = aws_proxy.s3_object_key
    with open('config.json', 'w', encoding="utf-8") as config_file:
        json.dump(data, config_file, indent=4)

    print("Your OTA update configuration has been set up in the config file!")
    print("Would you like to run the update now?")
    if utils.handle_y_n():
        run_ota_update.create_ota_update()

    print("Thank you for using the OTA Setup CLI!")


if __name__ == '__main__':
    setup_ota_update()
