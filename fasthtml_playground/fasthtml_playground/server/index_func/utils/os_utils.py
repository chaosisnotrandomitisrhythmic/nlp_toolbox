import json
import os
from dataclasses import asdict
from typing import Any, Dict, List

from loguru import logger
from opensearchpy import OpenSearch, RequestsHttpConnection

from index_func.datamodels.model import Insight
from index_func.datamodels.results import (
    CleanIndexCreateResult,
    IndexExistsResult,
    OverwriteIndexCreateResult,
    Result,
    SuccessResult,
    T,
)
from index_func.utils.generic_utils import batch

opensearch_password = os.getenv("OPENSEARCH_PASSWORD")


def connect_to_opensearch(
    host: str = "search-az-test-4-pcuj2jwp5f7jdjnm3gypboagu4.us-east-1.es.amazonaws.com",
    username: str = "andy",
    password: str = opensearch_password,
) -> OpenSearch:
    """
    Connect to OpenSearch.
    """
    return OpenSearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=(username, password),
        timeout=30,
        use_ssl=True,
        verify_certs=True,
        ssl_show_warn=False,
        connection_class=RequestsHttpConnection,
    )


def create_index(
    os_client: OpenSearch,
    index_name: str,
    overwrite: bool = False,
    body: Dict[str, Any] | None = None,
) -> Result[T]:
    """
    Create an index with the given name.
    """
    try:
        if os_client.indices.exists(index=index_name):
            if overwrite:
                os_client.indices.create(index=index_name, body=body)
                logger.success(f"Index {index_name} created and overwritten")
                return OverwriteIndexCreateResult(value=None)
            else:
                logger.warning(f"Index {index_name} already exists")
                return IndexExistsResult(value=None)
        else:
            os_client.indices.create(index=index_name, body=body)
            logger.success(f"Index {index_name} created")
            return CleanIndexCreateResult(value=None)
    except Exception as e:
        logger.error(f"Error creating index {index_name}: {repr(e)}")
        raise e


def update_mapping(
    os_client: OpenSearch,
    index_name: str,
    mapping: Dict[str, Any],
) -> Result[T]:
    """
    Update the mapping of an index.
    """
    try:
        response = os_client.indices.put_mapping(index=index_name, body=mapping)
        logger.success(f"Mapping updated for index {index_name}")
    except Exception as e:
        logger.error(f"Error updating mapping for index {index_name}: {repr(e)}")
        raise e


def verify_index_creation(
    os_client: OpenSearch,
    index_name: str,
) -> bool:
    """
    Verify that the index was created.
    """
    return os_client.indices.exists(index=index_name)


def delete_index(
    os_client: OpenSearch,
    index_name: str,
) -> Result[T]:
    """
    Delete the index.
    """
    try:
        os_client.indices.delete(index=index_name)
        logger.success(f"Index {index_name} deleted")
        return SuccessResult(value=None)
    except Exception as e:
        logger.error(f"Error deleting index {index_name}: {repr(e)}")
        raise e


def count_docs_in_index(
    os_client: OpenSearch,
    index_name: str,
) -> int:
    """
    Count the number of documents in the index.
    """
    return os_client.count(index=index_name)["count"]


def bulk_index(
    os_client: OpenSearch,
    index_name: str,
    documents: List[Insight],
    batch_size: int = 256,
) -> Result[T]:
    """
    Bulk index the documents.
    """

    assert batch_size % 2 == 0, "Batch size must be even"

    try:
        bulk_data = []
        for doc in documents:
            doc_data = asdict(doc)

            if not doc_data["docid"]:
                raise ValueError("docid is required")

            action = {"update": {"_index": index_name, "_id": doc_data["docid"]}}

            if doc.date:
                doc_data["date"] = doc.date.isoformat()

            # for upserting
            doc_action = {"doc": doc_data, "doc_as_upsert": True}

            # combine action and document data into a single line
            bulk_data.append(json.dumps(action, default=str))
            bulk_data.append(json.dumps(doc_action, default=str))

        # slpit data into batches and send bulk requests to CREATE
        for batch_item in batch(bulk_data, batch_size):
            response = os_client.bulk(index=index_name, body=batch_item)

            # handle errors gracefully
            result_errors = []
            if response["errors"]:
                for item in response["items"]:
                    if "error" not in item["create"]:
                        continue

                    reason = item["create"]["error"]
                    result_errors.append(item)
                    logger.debug(
                        f"Error indexing doc with id {item['create']['_id']}: {reason}"
                    )

        return SuccessResult(value=result_errors)

    except Exception as e:
        logger.error(f"failed to bulk index documents: {repr(e)}")
        raise e


def list_fields(
    os_client: OpenSearch,
    index_name: str,
) -> List[str]:
    """
    List the fields with type in the index.
    """
    try:
        response = os_client.indices.get_mapping(index=index_name)
        return {
            k: v["type"]
            for k, v in response[index_name]["mappings"]["properties"].items()
        }
    except Exception as e:
        logger.error(f"Error listing fields for index {index_name}: {repr(e)}")
        raise e
