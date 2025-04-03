from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_iam as iam,
)
import aws_cdk as cdk
from constructs import Construct

class AwsCdkEc2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        # Example VPC
        vpc = ec2.Vpc(self, "MyVpc",
            max_azs=1  # Default is all AZs in the region
        )
        # Example Security Group
        security_group = ec2.SecurityGroup(self, "MySecurityGroup",
            vpc=vpc,
            allow_all_outbound=True,
            description="Allow SSH access",
            security_group_name="MySecurityGroup"
        )

        # Lookup an existing key pair by name
        key_pair = ec2.KeyPair.from_key_pair_attributes(self, "MyKeyPair",
            key_pair_name="my-key-pair-ohio",  # Replace with your key pair name
        )

        # Example EC2 Instance
        instance = ec2.Instance(self, "MyInstance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            vpc=vpc,
            security_group=security_group,
            key_pair=key_pair
        )
        # Example EBS Volume
        volume = ec2.CfnVolume(self, "MyVolume",
            availability_zone=vpc.availability_zones[0],
            size=8,  # Size in GiB
            volume_type="gp2"  # General Purpose SSD
        )
        # Attach the volume to the instance
        ec2.CfnVolumeAttachment(self, "MyVolumeAttachment",
            instance_id=instance.instance_id,
            volume_id=volume.ref,
            device="/dev/sdh"  # Device name
        )
        # Example S3 Bucket
        
        bucket = s3.Bucket(self, "MyBucket",
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # NOT recommended for production code
            auto_delete_objects=True  # NOT recommended for production code
        )
        # Example IAM Role
        
        role = iam.Role(self, "MyRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
            ]
        )
        # Attach the role to the instance
        instance.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"))

