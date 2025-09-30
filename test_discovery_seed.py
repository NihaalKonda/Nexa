#!/usr/bin/env python3
"""Test script for discovery_seed module"""

import os
from src.discovery_seed import stub_suppliers, save_suppliers, load_suppliers

def test_discovery_seed():
    """Test the discovery seed functionality"""
    print("=" * 60)
    print("TESTING DISCOVERY SEED SAVE/LOAD")
    print("=" * 60)
    
    # Test creating stub suppliers and saving/loading
    print("\n1. Creating stub suppliers...")
    suppliers = stub_suppliers()
    
    print("\n2. Saving to JSON...")
    output_file = "data/test_suppliers.json"
    save_suppliers(suppliers, output_file)
    
    print("\n3. Loading from JSON...")
    loaded_suppliers = load_suppliers(output_file)
    
    print("\n4. Verification:")
    print(f"Original count: {len(suppliers)}")
    print(f"Loaded count: {len(loaded_suppliers)}")
    print(f"First supplier: {loaded_suppliers[0]['name']} -> {loaded_suppliers[0]['domain']}")
    
    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"\n5. Cleaned up test file: {output_file}")

if __name__ == "__main__":
    test_discovery_seed()