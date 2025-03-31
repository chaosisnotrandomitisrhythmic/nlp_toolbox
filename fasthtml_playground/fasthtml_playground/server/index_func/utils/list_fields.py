from index_func.utils.os_utils import connect_to_opensearch, list_fields

if __name__ == "__main__":
    os_client = connect_to_opensearch()
    fields = list_fields(os_client, "insights_test_1")
    print(fields)
