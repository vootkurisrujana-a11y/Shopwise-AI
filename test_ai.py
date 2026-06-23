import ai_engine

def run_tests():
    test_cases = [
        {
            "query": "Suggest a phone under ₹20,000 with a good camera",
            "expected_category": "phone",
            "expected_budget": 20000.0,
            "expected_keyword": "camera"
        },
        {
            "query": "I need a laptop under 50k for coding",
            "expected_category": "laptop",
            "expected_budget": 50000.0,
            "expected_keyword": "coding"
        },
        {
            "query": "Noise cancelling headphones below 10,000",
            "expected_category": "headphone",
            "expected_budget": 10000.0,
            "expected_keyword": "audio"
        },
        {
            "query": "Suggest a high rating smartwatch with GPS",
            "expected_category": "smartwatch",
            "expected_budget": None,
            "expected_keyword": "rating"
        }
    ]

    print("=" * 60)
    print("RUNNING NATURAL LANGUAGE QUERY PARSER TESTS")
    print("=" * 60)
    
    passed_count = 0
    for idx, tc in enumerate(test_cases, 1):
        parsed = ai_engine.parse_query(tc["query"])
        
        cat_ok = parsed["category"] == tc["expected_category"]
        budget_ok = parsed["budget"] == tc["expected_budget"]
        kw_ok = tc["expected_keyword"] in parsed["keywords"]
        
        status = "PASSED" if (cat_ok and budget_ok and kw_ok) else "FAILED"
        if status == "PASSED":
            passed_count += 1
            
        print(f"Test #{idx}: '{tc['query']}'")
        print(f"  Parsed: Category={parsed['category']}, Budget={parsed['budget']}, Keywords={parsed['keywords']}")
        print(f"  Expected: Category={tc['expected_category']}, Budget={tc['expected_budget']}, Keyword={tc['expected_keyword']}")
        print(f"  Status: {status} (Category: {'OK' if cat_ok else 'FAIL'}, Budget: {'OK' if budget_ok else 'FAIL'}, Keywords: {'OK' if kw_ok else 'FAIL'})")
        print("-" * 60)
        
    print(f"Test Summary: {passed_count}/{len(test_cases)} Passed.")
    print("=" * 60)
    
    assert passed_count == len(test_cases), "Some parser tests failed!"
    print("All NLP parser tests passed successfully!")

if __name__ == "__main__":
    run_tests()
