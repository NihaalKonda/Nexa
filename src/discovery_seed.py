"""
Discovery seed module for loading supplier data from CSV files or creating stub suppliers.
"""

import csv
import hashlib
import json
import tldextract
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse


def generate_supplier_id(name: str, domain: str) -> str:
    """
    Generate a unique supplier ID based on name and domain.
    
    Args:
        name: Supplier name
        domain: Supplier domain
        
    Returns:
        Hashed supplier ID
    """
    combined = f"{name.lower().strip()}|{domain.lower().strip()}"
    return hashlib.md5(combined.encode()).hexdigest()


def normalize_domain(website: str) -> Optional[str]:
    """
    Extract and normalize domain from a website URL.
    
    Args:
        website: Raw website URL
        
    Returns:
        Normalized domain or None if invalid
    """
    if not website:
        return None
        
    # Add protocol if missing
    if not website.startswith(('http://', 'https://')):
        website = 'https://' + website
        
    try:
        parsed = urlparse(website)
        if not parsed.netloc:
            return None
            
        # Use tldextract for better domain parsing
        extracted = tldextract.extract(website)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
        return None
        
    except Exception:
        return None


def load_suppliers_from_csv(
    csv_path: str,
    name_col: str = "name",
    website_col: str = "website", 
    country_col: str = "country",
    state_col: str = "state"
) -> List[Dict]:
    """
    Load suppliers from CSV file and normalize the data.
    
    Args:
        csv_path: Path to CSV file
        name_col: Column name for supplier name
        website_col: Column name for website
        country_col: Column name for country
        state_col: Column name for state
        
    Returns:
        List of normalized supplier dictionaries
    """
    suppliers = []
    seen_combinations = set()  # For deduplication
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Extract and validate required fields
                    name = row.get(name_col, '').strip()
                    website = row.get(website_col, '').strip()
                    
                    if not name or not website:
                        print(f"Row {row_num}: Missing required fields (name or website)")
                        continue
                    
                    # Normalize domain
                    domain = normalize_domain(website)
                    if not domain:
                        print(f"Row {row_num}: Invalid website URL: {website}")
                        continue
                    
                    # Check for duplicates
                    dedup_key = f"{name.lower()}|{domain.lower()}"
                    if dedup_key in seen_combinations:
                        print(f"Row {row_num}: Duplicate supplier: {name} - {domain}")
                        continue
                    seen_combinations.add(dedup_key)
                    
                    # Create supplier record
                    supplier = {
                        'supplier_id': generate_supplier_id(name, domain),
                        'name': name,
                        'domain': domain,
                        'country': row.get(country_col, '').strip() or None,
                        'state': row.get(state_col, '').strip() or None,
                        'sources': ['SEED_CSV'],
                        'last_seen_at': datetime.utcnow().isoformat() + 'Z'
                    }
                    
                    suppliers.append(supplier)
                    
                except Exception as e:
                    print(f"Row {row_num}: Error processing row: {e}")
                    continue
                    
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    except Exception as e:
        raise Exception(f"Error reading CSV file: {e}")
    
    print(f"Loaded {len(suppliers)} suppliers from CSV")
    return suppliers


def stub_suppliers() -> List[Dict]:
    """
    Create a minimal seed list of suppliers for testing the pipeline.
    
    Returns:
        List of stub supplier dictionaries
    """
    stub_data = [
        {
            'name': 'McMaster-Carr',
            'domain': 'mcmaster.com',
            'country': 'US',
            'state': 'IL'
        },
        {
            'name': 'Grainger',
            'domain': 'grainger.com', 
            'country': 'US',
            'state': 'IL'
        },
        {
            'name': 'US Plastic Corp',
            'domain': 'usplastic.com',
            'country': 'US',
            'state': 'OH'
        },
        {
            'name': 'Professional Plastics',
            'domain': 'professionalplastics.com',
            'country': 'US',
            'state': 'CA'
        },
        {
            'name': 'Curbell Plastics',
            'domain': 'curbellplastics.com',
            'country': 'US', 
            'state': 'NY'
        }
    ]
    
    suppliers = []
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    for stub in stub_data:
        supplier = {
            'supplier_id': generate_supplier_id(stub['name'], stub['domain']),
            'name': stub['name'],
            'domain': stub['domain'],
            'country': stub['country'],
            'state': stub['state'],
            'sources': ['STUB'],
            'last_seen_at': timestamp
        }
        suppliers.append(supplier)
    
    print(f"Generated {len(suppliers)} stub suppliers")
    return suppliers


def save_suppliers(suppliers: List[Dict], output_path: str) -> None:
    """
    Save suppliers list to JSON file.
    
    Args:
        suppliers: List of supplier dictionaries
        output_path: Path to output JSON file
    """
    try:
        with open(output_path, 'w') as file:
            json.dump(suppliers, file, indent=2)
        print(f"Saved {len(suppliers)} suppliers to {output_path}")
    except Exception as e:
        raise Exception(f"Error saving suppliers: {e}")


def load_suppliers(input_path: str) -> List[Dict]:
    """
    Load suppliers from JSON file.
    
    Args:
        input_path: Path to suppliers JSON file
        
    Returns:
        List of supplier dictionaries
    """
    try:
        with open(input_path, 'r') as file:
            suppliers = json.load(file)
        print(f"Loaded {len(suppliers)} suppliers from {input_path}")
        return suppliers
    except FileNotFoundError:
        raise FileNotFoundError(f"Suppliers file not found: {input_path}")
    except Exception as e:
        raise Exception(f"Error loading suppliers: {e}")


if __name__ == "__main__":
    # Test the functions
    print("=" * 60)
    print("TESTING DISCOVERY SEED MODULE")  
    print("=" * 60)
    
    # Test stub suppliers
    print("\n1. Testing stub suppliers:")
    stub_suppliers_list = stub_suppliers()
    for supplier in stub_suppliers_list[:2]:  # Show first 2
        print(f"  {supplier['name']} -> {supplier['domain']} ({supplier['supplier_id'][:8]}...)")
    
    # Test domain normalization
    print("\n2. Testing domain normalization:")
    test_urls = [
        "https://example.com",
        "example.com", 
        "www.example.com",
        "http://sub.example.co.uk",
        "invalid-url"
    ]
    for url in test_urls:
        normalized = normalize_domain(url)
        print(f"  {url} -> {normalized}")
    
    # Test CSV structure (create a sample file)
    print("\n3. Testing CSV functionality (creating sample):")
    sample_csv = "data/sample_suppliers.csv"
    
    # Create sample CSV for testing
    import os
    os.makedirs('data', exist_ok=True)
    
    with open(sample_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'website', 'country', 'state'])
        writer.writerow(['Test Corp', 'https://test.com', 'US', 'CA'])
        writer.writerow(['Example Ltd', 'example.co.uk', 'UK', ''])
        writer.writerow(['', 'invalid.com', 'US', 'TX'])  # Missing name - should skip
        writer.writerow(['Duplicate Corp', 'test.com', 'US', 'NY'])  # Duplicate domain
    
    # Load the sample CSV
    try:
        csv_suppliers = load_suppliers_from_csv(sample_csv)
        print(f"  Successfully loaded {len(csv_suppliers)} suppliers from sample CSV")
        for supplier in csv_suppliers:
            print(f"    {supplier['name']} -> {supplier['domain']}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Clean up
    if os.path.exists(sample_csv):
        os.remove(sample_csv)