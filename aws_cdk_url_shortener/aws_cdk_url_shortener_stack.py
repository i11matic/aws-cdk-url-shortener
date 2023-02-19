from aws_cdk import (
    # Duration,
    Stack,
    aws_ecr as ecr,
    # aws_sqs as sqs,
    aws_lambda as lambda_,
    aws_iam as iam,
)
from constructs import Construct
import yaml


class AwsCdkUrlShortenerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        with open("./configs/version.yaml", "r") as config:
            lambda_image_config = yaml.safe_load(config)
        repo = ecr.Repository.from_repository_name(
            self, "Repository", repository_name=lambda_image_config["image"]
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

        lambda_.DockerImageFunction(
            self,
            "urls-shortener-lambda",
            code=lambda_.DockerImageCode.from_ecr(
                repository=repo, tag_or_digest=lambda_image_config["tag"]
            ),
            role=lambda_role,
        )
