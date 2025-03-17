import argparse
import shutil

import boto3
from loguru import logger
from sagemaker.pytorch import PyTorchModel
from sagemaker.serverless import ServerlessInferenceConfig
from config import (
    SERVERLESS_CONFIG,
    ENDPOINT_NAME,
    SAGEMAKER_ROLE,
    S3_BUCKET,
    MODEL_NAME,
    MODEL_TYPE,
)

from rerankers import Reranker


def download_and_package_model(
    model_name: str,
    model_type: str,
) -> None:
    """
    Downloads a model and packages it into a tar.gz archive.

    Args:
        model_name: The name/path of the model to download
        model_type: The type of the model (e.g., "colbert")
        output_dir: Directory where the model will be saved
        archive_name: Name of the output archive file (without extension)
    """
    # Download and save model
    ranker = Reranker(model_name, model_type=model_type)
    ranker.model.save_pretrained(f"model/{MODEL_NAME.replace('/', '-')}")
    ranker.tokenizer.save_pretrained(f"model/{MODEL_NAME.replace('/', '-')}")
    # Create tar.gz archive
    shutil.make_archive("model", "gztar", "model")
    logger.info("Successfully created model.tar.gz")


def upload_model_to_s3(bucket: str = S3_BUCKET) -> None:
    """
    Uploads a model archive to S3.

    Args:
        file_name: Name of the archive file to upload
        bucket: Name of the S3 bucket to upload to
    """
    s3_client = boto3.client("s3")
    s3_key = f"rerankers/{MODEL_NAME.replace('/', '-')}/model.tar.gz"
    s3_client.upload_file("model.tar.gz", bucket, s3_key)
    logger.info(f"Successfully uploaded model.tar.gz to s3://{bucket}/{s3_key}")


def deploy_model() -> None:
    """
    Deploys the PyTorch model to SageMaker as a serverless endpoint.
    """
    model = PyTorchModel(
        name=f"mdl-nlp-reranker-{MODEL_NAME.replace('/', '-')}",
        model_data=f"s3://{S3_BUCKET}/rerankers/{MODEL_NAME.replace('/', '-')}/model.tar.gz",
        role=SAGEMAKER_ROLE,
        entry_point="inference.py",
        framework_version="2.1.0",
        py_version="py310",
        source_dir="source_code",
    )

    # Configure serverless inference
    serverless_config = ServerlessInferenceConfig(**SERVERLESS_CONFIG)

    model.deploy(
        serverless_inference_config=serverless_config,
        endpoint_name=ENDPOINT_NAME,
    )
    logger.info(f"Successfully deployed model to endpoint: {ENDPOINT_NAME}")


def teardown_endpoint() -> None:
    """
    Tears down the SageMaker endpoint completely, including all configurations.
    This will delete both the endpoint and the endpoint configuration.
    """
    sagemaker_client = boto3.client("sagemaker")

    try:
        # Delete the endpoint
        sagemaker_client.delete_endpoint(EndpointName=ENDPOINT_NAME)
        logger.info(f"Successfully deleted endpoint: {ENDPOINT_NAME}")

        # Delete the endpoint configuration
        sagemaker_client.delete_endpoint_config(EndpointConfigName=ENDPOINT_NAME)
        logger.info(f"Successfully deleted endpoint configuration: {ENDPOINT_NAME}")

        # Delete the model
        sagemaker_client.delete_model(
            ModelName=f"mdl-nlp-reranker-{MODEL_NAME.replace('/', '-')}"
        )
        logger.info(
            f"Successfully deleted model: {f'mdl-nlp-reranker-{MODEL_NAME.replace('/', '-')}'}"
        )
    except Exception as e:
        logger.error(f"Error during endpoint teardown: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Deploy or teardown SageMaker endpoint"
    )
    parser.add_argument(
        "action",
        choices=["deploy", "teardown"],
        help="Action to perform: deploy (spin up endpoint) or teardown (clean up)",
        required=True,
    )

    args = parser.parse_args()

    if args.action == "deploy":
        download_and_package_model(MODEL_NAME, MODEL_TYPE)
        upload_model_to_s3(S3_BUCKET)
        deploy_model()
    else:  # teardown
        teardown_endpoint()
