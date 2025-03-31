import json

from loguru import logger

from index_func.utils.os_utils import connect_to_opensearch

if __name__ == "__main__":
    INDEX_NAME = "insights_test_1"

    # Connect to OpenSearch
    os_client = connect_to_opensearch()

    # log all fields in the index
    response = os_client.indices.get_mapping(index=INDEX_NAME)
    logger.info(f"Fields in index {INDEX_NAME}:")
    logger.info(json.dumps(response, indent=2))
