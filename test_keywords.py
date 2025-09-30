#!/usr/bin/env python3
"""Test script for keywords module"""

from src.keywords import expand_keywords, extract_specifications, get_industry_terms

def test_keywords():
    """Test the keywords functionality"""
    print("=" * 60)
    print("TESTING KEYWORDS MODULE")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        "PETG sheet 2mm ISO 9001 medical grade",
        "PVC gasket 5mm thick automotive",
        "nylon rod 10mm diameter FDA approved",
        "PTFE film 0.5mm aerospace application"
    ]
    
    for query in test_cases:
        print(f"\nQuery: {query}")
        print(f"Expanded: {expand_keywords(query)}")
        print(f"Specs: {extract_specifications(query)}")
        print(f"Industry: {get_industry_terms(query)}")
        print("-" * 40)

if __name__ == "__main__":
    test_keywords()