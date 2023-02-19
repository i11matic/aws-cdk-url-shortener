#!/usr/bin/env python3
import aws_cdk as cdk

from aws_cdk_url_shortener.aws_cdk_url_shortener_stack import (
    AwsCdkUrlShortenerStack,
)


app = cdk.App()
AwsCdkUrlShortenerStack(
    app,
    "AwsCdkUrlShortenerStack",
    env=cdk.Environment(account="766251705079", region="us-west-2"),
)
app.synth()
