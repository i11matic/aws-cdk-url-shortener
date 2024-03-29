from aws_cdk import (
    # Duration,
    Stack,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    aws_lambda as lambda_,
    aws_iam as iam,
)
from constructs import Construct
import yaml


class AwsCdkUrlShortenerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        with open("./configs/config.yaml", "r") as config:
            lambda_image_config = yaml.safe_load(config)
        repo = ecr.Repository.from_repository_name(
            self, "Repository", repository_name=lambda_image_config["image"]
        )

        target_vpc = ec2.Vpc.from_lookup(self, "VPC", is_default=True)

        vpc_subnets = ec2.SubnetSelection(
            subnets=target_vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ).subnets
        )

        lambda_role = iam.Role(
            self,
            "awsLambdaUrlShortener",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonDynamoDBFullAccess"
            )
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonEC2FullAccess"
            )
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaRole"
            )
        )

        url_shortener = lambda_.DockerImageFunction(
            self,
            "urls-shortener-lambda",
            code=lambda_.DockerImageCode.from_ecr(
                repository=repo, tag_or_digest=lambda_image_config["tag"]
            ),
            role=lambda_role,
            vpc=target_vpc,
            vpc_subnets=vpc_subnets,
            environment={
             "DAX_ENDPOINT": lambda_image_config["daxEndpoint"]
            }
        )
        version = url_shortener.current_version
        lambda_.Alias(
            self,
            "LambdaAlias",
            alias_name=lambda_image_config["alias"],
            version=version,
        )
