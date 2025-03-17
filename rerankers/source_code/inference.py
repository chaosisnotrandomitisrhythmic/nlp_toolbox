import os
import json
from typing import Dict, Any
from rerankers import Reranker
from loguru import logger

MODEL_NAME = "answerdotai/answerai-colbert-small-v1"


def model_fn(model_dir: str) -> Reranker:
    """
    Load the model for inference.
    """
    # Log what is inside model_dir
    logger.info(f"HELL YEAH:::Model directory: {model_dir}")
    logger.info(f"HELL YEAH:::Contents of model directory: {os.listdir(model_dir)}")

    # Initialize the reranker with the local path
    model_path = os.path.join(model_dir, MODEL_NAME.replace("/", "-"))
    logger.info(f"HELL YEAH:::Loading model from: {model_path}")

    ranker = Reranker(
        model_path,
        model_type="colbert",
    )
    return ranker


def input_fn(request_body: str, request_content_type: str) -> Dict[str, Any]:
    """
    Deserialize and prepare the prediction input.
    """
    if request_content_type != "application/json":
        raise ValueError(f"Unsupported content type: {request_content_type}")

    # Parse the input JSON
    input_data = json.loads(request_body)

    # Validate required fields
    required_fields = ["query", "docs", "doc_ids"]
    for field in required_fields:
        if field not in input_data:
            raise ValueError(f"Missing required field: {field}")

    return input_data


def predict_fn(input_data: Dict[str, Any], model: Reranker) -> Any:
    """
    Apply model to the incoming request.
    """
    query = input_data["query"]
    docs = input_data["docs"]
    doc_ids = input_data["doc_ids"]

    # Optional parameters with defaults
    k = input_data.get("k", len(docs))  # Default to all docs if k not specified

    # Perform the ranking
    ranked_results = model.rank(query=query, docs=docs, doc_ids=doc_ids)
    logger.info(f"HELL YEAH:::Ranked results: {ranked_results}")

    # Get top k results - ranked_results is already a RankedResults object
    # Convert Result objects to serializable dictionary
    return {
        "rankings": [
            {
                "doc_id": result.doc_id,
                "score": float(
                    result.score
                ),  # Convert score to float for JSON serialization
            }
            for result in ranked_results.results[:k]
        ]
    }


def output_fn(prediction: Any, response_content_type: str) -> str:
    """
    Serialize and prepare the prediction output.
    """
    if response_content_type != "application/json":
        raise ValueError(f"Unsupported content type: {response_content_type}")

    return json.dumps(prediction)
