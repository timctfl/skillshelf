from processor.preprocessor import preprocess
from exporter.export import export_output


def mock_llm_enrichment(data):
    """
    Simulates LLM enrichment layer
    """
    data["added_tags"] = ["sportswear", "fitness", "activewear"]
    data["taxonomy"] = {
        "category": "Apparel",
        "subcategory": "Sportswear"
    }
    return data


def test_pipeline():
    input_data = {
        "title": "sports-attire",
        "tags": ["clothes", "clothes", "cotton", "outdoor"]
    }

    # Step 1: Preprocess
    processed = preprocess(input_data)

    # Step 2: Simulate LLM
    enriched = mock_llm_enrichment(processed)

    # Step 3: Export
    csv_out = export_output(enriched, "csv")
    table_out = export_output(enriched, "table")

    assert "sportswear" in csv_out
    assert "sportswear" in table_out

    print("✅ End-to-end pipeline working")


if __name__ == "__main__":
    test_pipeline()