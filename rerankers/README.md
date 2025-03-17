# SageMaker Reranker Deployment

## Overview

This project provides tools to deploy and test reranking models on AWS SageMaker serverless endpoints. It includes functionality for model packaging, deployment, and latency testing.

This project heavily relies on [Answer.ai's rerankers library](https://github.com/AnswerDotAI/rerankers), a lightweight unified API that simplifies working with various reranking models. The library provides a single consistent interface for multiple reranking approaches including cross-encoders, RankGPT, ColBERT, T5-based rerankers, and API services like Cohere and Pinecone, making it easy to experiment with different reranking strategies without changing your application code.

## Requirements

- Python 3.8+
- AWS Account with appropriate permissions

## Usage

### Deployment

Deploy the model to SageMaker:

```bash
pip install -r requirements.txt
python deploy.py deploy
```

Tear down the endpoint:

```bash
python deploy.py teardown
```

### Testing

The repository includes a Jupyter notebook (`test_endpoint.ipynb`) for testing endpoint latency and performance.


## API Format

The endpoint accepts JSON requests with the following structure:

```json
{
    "query": "your search query",
    "docs": ["document1", "document2", ...],
    "doc_ids": ["id1", "id2", ...],
    "k": 10  // optional, number of results to return
}
```

Response format:

```json
{
    "rankings": [
        {
            "doc_id": "id1",
            "score": 0.95
        },
        ...
    ]
}
```
```

