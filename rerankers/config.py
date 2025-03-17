# Model configuration
MODEL_TYPE = "colbert"
MODEL_NAME = "answerdotai/answerai-colbert-small-v1"
S3_BUCKET = "sagemaker-bucket-666"

# Endpoint configuration
ENDPOINT_NAME = "reranker-endpoint-1"
SAGEMAKER_ROLE = "arn:aws:iam::462019928087:role/service-role/SageMaker-ExecutionRole-20250114T174456"

# Serverless configuration
SERVERLESS_CONFIG = {
    "memory_size_in_mb": 6144,
    "max_concurrency": 1,
}
