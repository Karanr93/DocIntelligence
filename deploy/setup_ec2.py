"""Create EC2 instance with security group and key pair for DocClause deployment."""
import boto3
import os
import time
import json

# Config
REGION = "us-east-1"
INSTANCE_TYPE = "t3.micro"  # ~$7.60/month, 2 vCPU, 1GB RAM
AMI_ID = None  # Will auto-detect Amazon Linux 2023
KEY_NAME = "docclause-key"
SG_NAME = "docclause-sg"
INSTANCE_NAME = "DocClause-Server"

# Load AWS creds from backend .env
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
load_dotenv(env_path)

AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY")

ec2 = boto3.client("ec2", region_name=REGION,
                    aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET)
ec2_resource = boto3.resource("ec2", region_name=REGION,
                               aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET)


def get_amazon_linux_ami():
    """Get latest Amazon Linux 2023 AMI."""
    response = ec2.describe_images(
        Owners=["amazon"],
        Filters=[
            {"Name": "name", "Values": ["al2023-ami-2023*-x86_64"]},
            {"Name": "state", "Values": ["available"]},
            {"Name": "architecture", "Values": ["x86_64"]},
        ]
    )
    images = sorted(response["Images"], key=lambda x: x["CreationDate"], reverse=True)
    if not images:
        raise Exception("No Amazon Linux 2023 AMI found")
    ami = images[0]
    print(f"AMI: {ami['ImageId']} ({ami['Name']})")
    return ami["ImageId"]


def create_key_pair():
    """Create or reuse SSH key pair."""
    key_file = os.path.join(os.path.dirname(__file__), f"{KEY_NAME}.pem")

    # Check if key already exists
    try:
        ec2.describe_key_pairs(KeyNames=[KEY_NAME])
        print(f"Key pair '{KEY_NAME}' already exists")
        if os.path.exists(key_file):
            return key_file
        else:
            # Delete and recreate since we don't have the .pem
            ec2.delete_key_pair(KeyName=KEY_NAME)
            print(f"  Deleted old key (missing .pem file), recreating...")
    except ec2.exceptions.ClientError:
        pass  # Key doesn't exist

    response = ec2.create_key_pair(KeyName=KEY_NAME)
    with open(key_file, "w") as f:
        f.write(response["KeyMaterial"])
    print(f"Created key pair: {key_file}")
    return key_file


def create_security_group():
    """Create security group allowing HTTP (80) and SSH (22)."""
    # Check if SG exists
    try:
        response = ec2.describe_security_groups(GroupNames=[SG_NAME])
        sg_id = response["SecurityGroups"][0]["GroupId"]
        print(f"Security group '{SG_NAME}' already exists: {sg_id}")
        return sg_id
    except ec2.exceptions.ClientError:
        pass

    # Get default VPC
    vpcs = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])
    vpc_id = vpcs["Vpcs"][0]["VpcId"]

    response = ec2.create_security_group(
        GroupName=SG_NAME,
        Description="DocClause web application - HTTP and SSH access",
        VpcId=vpc_id
    )
    sg_id = response["GroupId"]

    # Allow SSH (port 22) and HTTP (port 80) from anywhere
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "SSH access"}]
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 80,
                "ToPort": 80,
                "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTP access"}]
            },
        ]
    )
    print(f"Created security group: {sg_id} (SSH + HTTP open)")
    return sg_id


def launch_instance(ami_id, sg_id):
    """Launch EC2 instance."""
    # Check for existing running instance with the same name
    response = ec2.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [INSTANCE_NAME]},
            {"Name": "instance-state-name", "Values": ["running", "stopped", "pending"]}
        ]
    )
    for reservation in response["Reservations"]:
        for inst in reservation["Instances"]:
            print(f"Instance '{INSTANCE_NAME}' already exists: {inst['InstanceId']} ({inst['State']['Name']})")
            if inst["State"]["Name"] == "stopped":
                ec2.start_instances(InstanceIds=[inst["InstanceId"]])
                print("  Starting stopped instance...")
            return inst["InstanceId"]

    # User data script to install dependencies on boot
    user_data = """#!/bin/bash
set -e

# Update system
dnf update -y

# Install Python 3.11, pip, git
dnf install -y python3.11 python3.11-pip git nginx

# Create symlinks
ln -sf /usr/bin/python3.11 /usr/bin/python3
ln -sf /usr/bin/pip3.11 /usr/bin/pip3

# Install Node.js 18
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
dnf install -y nodejs

# Create app directory
mkdir -p /opt/docclause
chown ec2-user:ec2-user /opt/docclause

echo "SETUP COMPLETE" > /tmp/setup_done.txt
"""

    instances = ec2_resource.create_instances(
        ImageId=ami_id,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroupIds=[sg_id],
        MinCount=1,
        MaxCount=1,
        UserData=user_data,
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": INSTANCE_NAME}]
        }],
        # Add IAM instance profile for Bedrock access if available
    )

    instance = instances[0]
    print(f"Launched instance: {instance.id}")

    # Wait for running
    print("Waiting for instance to start...")
    instance.wait_until_running()
    instance.reload()
    print(f"Instance running: {instance.public_ip_address}")

    return instance.id


def allocate_elastic_ip(instance_id):
    """Allocate and associate an Elastic IP."""
    # Check for existing EIP
    eips = ec2.describe_addresses(
        Filters=[{"Name": "instance-id", "Values": [instance_id]}]
    )
    if eips["Addresses"]:
        eip = eips["Addresses"][0]["PublicIp"]
        print(f"Elastic IP already attached: {eip}")
        return eip

    # Check for unattached EIPs we own
    all_eips = ec2.describe_addresses(
        Filters=[{"Name": "tag:Name", "Values": ["DocClause-EIP"]}]
    )
    if all_eips["Addresses"]:
        alloc_id = all_eips["Addresses"][0]["AllocationId"]
        eip = all_eips["Addresses"][0]["PublicIp"]
    else:
        response = ec2.allocate_address(
            Domain="vpc",
            TagSpecifications=[{
                "ResourceType": "elastic-ip",
                "Tags": [{"Key": "Name", "Value": "DocClause-EIP"}]
            }]
        )
        alloc_id = response["AllocationId"]
        eip = response["PublicIp"]
        print(f"Allocated Elastic IP: {eip}")

    # Associate with instance
    ec2.associate_address(AllocationId=alloc_id, InstanceId=instance_id)
    print(f"Associated Elastic IP {eip} with instance {instance_id}")

    return eip


def main():
    print("=" * 50)
    print("DocClause EC2 Deployment")
    print("=" * 50)

    # Step 1: Get AMI
    print("\n[1/5] Finding Amazon Linux 2023 AMI...")
    ami_id = get_amazon_linux_ami()

    # Step 2: Create key pair
    print("\n[2/5] Creating SSH key pair...")
    key_file = create_key_pair()

    # Step 3: Create security group
    print("\n[3/5] Creating security group...")
    sg_id = create_security_group()

    # Step 4: Launch instance
    print("\n[4/5] Launching EC2 instance...")
    instance_id = launch_instance(ami_id, sg_id)

    # Wait a moment for instance to be fully ready
    print("Waiting for instance to initialize...")
    time.sleep(10)

    # Step 5: Elastic IP
    print("\n[5/5] Setting up Elastic IP...")
    public_ip = allocate_elastic_ip(instance_id)

    # Summary
    print("\n" + "=" * 50)
    print("EC2 INFRASTRUCTURE READY!")
    print("=" * 50)
    print(f"Instance ID:  {instance_id}")
    print(f"Public IP:    {public_ip}")
    print(f"SSH Key:      {key_file}")
    print(f"SSH Command:  ssh -i {key_file} ec2-user@{public_ip}")
    print(f"Web URL:      http://{public_ip}")
    print(f"\nNote: Wait 2-3 minutes for the instance to finish installing dependencies.")

    # Save deployment info
    info = {
        "instance_id": instance_id,
        "public_ip": public_ip,
        "key_file": key_file,
        "region": REGION,
        "ssh_command": f"ssh -i {key_file} ec2-user@{public_ip}"
    }
    info_file = os.path.join(os.path.dirname(__file__), "deployment_info.json")
    with open(info_file, "w") as f:
        json.dump(info, f, indent=2)
    print(f"\nDeployment info saved to: {info_file}")


if __name__ == "__main__":
    main()
