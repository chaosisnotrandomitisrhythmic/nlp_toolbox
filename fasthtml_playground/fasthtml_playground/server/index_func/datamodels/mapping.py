index_mapping = {
    "settings": {
        "index": {
            "knn": True,
        }
    },
    "mappings": {
        "properties": {
            "docid": {"type": "keyword"},
            "insight": {"type": "text"},
            "product": {"type": "keyword"},
            "country": {"type": "keyword"},
            "region": {"type": "keyword"},
            "disease_area_indication": {"type": "keyword"},
            "az_therapeutic_area": {"type": "keyword"},
            "themes": {"type": "keyword"},
            "business_unit": {"type": "keyword"},
            "clinical_trial": {"type": "keyword"},
            "meeting": {"type": "keyword"},
            "transforming_care_project": {"type": "keyword"},
            "submitter": {"type": "keyword"},
            "product_topic": {"type": "keyword"},
            "veeva_theme": {"type": "keyword"},
            "sentiment_score": {"type": "half_float"},
            "disease_indication_1": {"type": "keyword"},
            "disease_indication_2": {"type": "keyword"},
            "disease_indication_3": {"type": "keyword"},
            "disease_indication_4": {"type": "keyword"},
            "disease_indication_5": {"type": "keyword"},
            "date": {
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
            },
            "insight_vector": {
                "type": "knn_vector",
                "dimension": 384,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "faiss",
                    "parameters": {"ef_construction": 100, "m": 16},
                },
            },
        },
    },
}
