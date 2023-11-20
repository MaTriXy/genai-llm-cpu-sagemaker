#!/usr/bin/env python3
import os
import boto3
import aws_cdk as cdk
import time

from infrastructure.model_serving_stack import ModelServingStack
from infrastructure.image_building_stack import ImageBuildingStack
from infrastructure.model_download_stack import ModelDownloadStack


environment=cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"],
    region=os.environ["CDK_DEFAULT_REGION"])

config = {
    "model_bucket_prefix": "model-bucket",
    "project_name": "llm-cpu",
    "repository_name": "model-image-repository",
    "image_bucket_name": "image-bucket",
    "sagemaker_role_name": "sagemaker-execution-role",
    "instance_type": "ml.c7g.2xlarge",
    "model_bucket_key": "llama-2-7b-chat.tar.gz",
    "sagemaker_model_name": "llamacpp-arm64-c7-x8-v00" #TODO obsolete
}

app = cdk.App()

modelDownloadStack = ModelDownloadStack(app, 
    "ModelDownloadStack", 
    env=environment, 
    model_bucket_prefix=config["model_bucket_prefix"],
    project_name=config["project_name"],
    )

imageBuildingStack = ImageBuildingStack(app, 
    "ImageBuildingStack", 
    env=environment,
    project_name=config["project_name"], 
    repository_name=config["project_name"], 
    image_bucket_name=config["image_bucket_name"], 
    model_bucket_name=cdk.Fn.import_value("var-modelbucketname"),
    )

#time.sleep(15*60) #TODO wait for image to be built instead of time delay / resource creation

modelServingStack = ModelServingStack(app, 
    "ModelServingStack", 
    env=environment, 
    sagemaker_role_name=config["sagemaker_role_name"],
    instance_type=config["instance_type"], 
    model_repository_image=cdk.Fn.import_value("var-modelrepositoryuri"), 
    model_bucket_name=cdk.Fn.import_value("var-modelbucketname"), 
    model_bucket_key=config["model_bucket_key"], 
    sagemaker_model_name=config["sagemaker_model_name"]
    )

#TODO wait until SageMaker model is InService before configuring it

app.synth()
