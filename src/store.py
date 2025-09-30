"""
Store module for saving and loading product data in JSON and CSV formats.
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


def ensure_directory(file_path: str) -> None:
    """
    Ensure the directory for a file path exists.
    
    Args:
        file_path: File path to create directory for
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def save_json(data: Any, file_path: str, indent: int = 2) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        file_path: Path to JSON file
        indent: JSON indentation
    """
    ensure_directory(file_path)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=indent, ensure_ascii=False)
        print(f"Saved data to {file_path}")
    except Exception as e:
        raise Exception(f"Error saving JSON to {file_path}: {e}")


def load_json(file_path: str) -> Any:
    """
    Load data from JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"Loaded data from {file_path}")
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error loading JSON from {file_path}: {e}")


def flatten_product_for_csv(product: Dict) -> Dict[str, Any]:
    """
    Flatten a product dictionary for CSV export.
    
    Args:
        product: Product dictionary
        
    Returns:
        Flattened product dictionary
    """
    flattened = {}
    
    # Basic fields
    basic_fields = [
        'product_id', 'supplier_id', 'name', 'sku', 'mpn', 
        'price_text', 'datasheet_url', 'source_url', 'last_seen_at', 'score'
    ]
    
    for field in basic_fields:
        flattened[field] = product.get(field, '')
    
    # Certifications as comma-separated string
    certifications = product.get('certifications', [])
    flattened['certifications'] = ', '.join(certifications) if certifications else ''
    
    # Raw specifications as JSON string (for reference)
    specs_raw = product.get('specs_raw', {})
    flattened['specs_raw_json'] = json.dumps(specs_raw) if specs_raw else ''
    
    # Canonical specifications as individual columns
    specs_canonical = product.get('specs_canonical', {})
    
    # Common canonical spec fields
    canonical_fields = [
        'thickness_mm', 'width_mm', 'length_mm', 'height_mm', 'diameter_mm',
        'max_temp_c', 'operating_temp_c', 'melting_temp_c', 'glass_transition_c',
        'max_pressure_psi', 'working_pressure_psi',
        'density_g_cm3', 'hardness_shore_a', 'tensile_strength_psi',
        'elongation_percent', 'compression_set_percent',
        'color', 'grade', 'standard', 'type'
    ]
    
    for field in canonical_fields:
        flattened[field] = specs_canonical.get(field, '')
    
    return flattened


def save_products_csv(products: List[Dict], file_path: str) -> None:
    """
    Save products to CSV file.
    
    Args:
        products: List of product dictionaries
        file_path: Path to CSV file
    """
    if not products:
        print("No products to save to CSV")
        return
    
    ensure_directory(file_path)
    
    # Flatten all products
    flattened_products = [flatten_product_for_csv(product) for product in products]
    
    # Get all possible field names
    all_fields = set()
    for product in flattened_products:
        all_fields.update(product.keys())
    
    # Define field order (important fields first)
    field_priority = [
        'product_id', 'supplier_id', 'name', 'sku', 'mpn', 'score',
        'price_text', 'certifications', 
        'thickness_mm', 'width_mm', 'length_mm', 'diameter_mm',
        'max_temp_c', 'max_pressure_psi', 'color', 'grade',
        'datasheet_url', 'source_url', 'last_seen_at'
    ]
    
    # Order fields: priority fields first, then remaining alphabetically
    ordered_fields = []
    for field in field_priority:
        if field in all_fields:
            ordered_fields.append(field)
            all_fields.remove(field)
    ordered_fields.extend(sorted(all_fields))
    
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=ordered_fields)
            writer.writeheader()
            
            for product in flattened_products:
                # Ensure all fields are present (empty string for missing)
                row = {field: product.get(field, '') for field in ordered_fields}
                writer.writerow(row)
        
        print(f"Saved {len(products)} products to CSV: {file_path}")
        
    except Exception as e:
        raise Exception(f"Error saving CSV to {file_path}: {e}")


def load_products_csv(file_path: str) -> List[Dict]:
    """
    Load products from CSV file.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of product dictionaries
    """
    try:
        products = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                product = {}
                
                # Basic fields
                basic_fields = [
                    'product_id', 'supplier_id', 'name', 'sku', 'mpn',
                    'price_text', 'datasheet_url', 'source_url', 'last_seen_at'
                ]
                
                for field in basic_fields:
                    value = row.get(field, '').strip()
                    product[field] = value if value else None
                
                # Score as integer
                score_str = row.get('score', '').strip()
                product['score'] = int(score_str) if score_str.isdigit() else 0
                
                # Certifications from comma-separated string
                cert_str = row.get('certifications', '').strip()
                product['certifications'] = [c.strip() for c in cert_str.split(',') if c.strip()] if cert_str else []
                
                # Raw specs from JSON string
                specs_raw_str = row.get('specs_raw_json', '').strip()
                try:
                    product['specs_raw'] = json.loads(specs_raw_str) if specs_raw_str else {}
                except json.JSONDecodeError:
                    product['specs_raw'] = {}
                
                # Canonical specifications
                specs_canonical = {}
                canonical_fields = [
                    'thickness_mm', 'width_mm', 'length_mm', 'height_mm', 'diameter_mm',
                    'max_temp_c', 'operating_temp_c', 'melting_temp_c', 'glass_transition_c',
                    'max_pressure_psi', 'working_pressure_psi',
                    'density_g_cm3', 'hardness_shore_a', 'tensile_strength_psi',
                    'elongation_percent', 'compression_set_percent'
                ]
                
                # Numeric canonical fields
                for field in canonical_fields:
                    value_str = row.get(field, '').strip()
                    if value_str:
                        try:
                            specs_canonical[field] = float(value_str)
                        except ValueError:
                            pass
                
                # String canonical fields
                string_fields = ['color', 'grade', 'standard', 'type']
                for field in string_fields:
                    value = row.get(field, '').strip()
                    if value:
                        specs_canonical[field] = value
                
                product['specs_canonical'] = specs_canonical
                
                products.append(product)
        
        print(f"Loaded {len(products)} products from CSV: {file_path}")
        return products
        
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error loading CSV from {file_path}: {e}")


def save_products(products: List[Dict], json_path: Optional[str] = None, csv_path: Optional[str] = None) -> None:
    """
    Save products to both JSON and CSV formats.
    
    Args:
        products: List of product dictionaries
        json_path: Path to JSON file (optional)
        csv_path: Path to CSV file (optional)
    """
    if json_path:
        save_json(products, json_path)
    
    if csv_path:
        save_products_csv(products, csv_path)


def load_products(json_path: str) -> List[Dict]:
    """
    Load products from JSON file.
    
    Args:
        json_path: Path to JSON file
        
    Returns:
        List of product dictionaries
    """
    return load_json(json_path)


def create_summary_report(products: List[Dict], file_path: str) -> None:
    """
    Create a summary report of products.
    
    Args:
        products: List of product dictionaries
        file_path: Path to save report
    """
    if not products:
        return
    
    ensure_directory(file_path)
    
    # Calculate summary statistics
    total_products = len(products)
    products_with_datasheet = len([p for p in products if p.get('datasheet_url')])
    products_with_price = len([p for p in products if p.get('price_text')])
    products_with_specs = len([p for p in products if p.get('specs_raw') and len(p['specs_raw']) > 0])
    
    # Score distribution
    scores = [p.get('score', 0) for p in products]
    avg_score = sum(scores) / len(scores) if scores else 0
    min_score = min(scores) if scores else 0
    max_score = max(scores) if scores else 0
    
    # Top suppliers by product count
    supplier_counts = {}
    for product in products:
        supplier_id = product.get('supplier_id', 'unknown')
        supplier_counts[supplier_id] = supplier_counts.get(supplier_id, 0) + 1
    
    top_suppliers = sorted(supplier_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Most common specifications
    spec_counts = {}
    for product in products:
        for spec_key in product.get('specs_canonical', {}):
            spec_counts[spec_key] = spec_counts.get(spec_key, 0) + 1
    
    common_specs = sorted(spec_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Create report
    report = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'summary': {
            'total_products': total_products,
            'products_with_datasheet': products_with_datasheet,
            'products_with_price': products_with_price,
            'products_with_specifications': products_with_specs
        },
        'scores': {
            'average': round(avg_score, 2),
            'minimum': min_score,
            'maximum': max_score
        },
        'top_suppliers': [{'supplier_id': s[0], 'product_count': s[1]} for s in top_suppliers],
        'common_specifications': [{'spec': s[0], 'product_count': s[1]} for s in common_specs]
    }
    
    save_json(report, file_path)
    print(f"Created summary report: {file_path}")


if __name__ == "__main__":
    # Test the store functionality
    print("=" * 60)
    print("TESTING STORE MODULE")
    print("=" * 60)
    
    # Create test products
    test_products = [
        {
            'product_id': 'test1',
            'supplier_id': 'supplier1', 
            'name': 'PETG Sheet 2mm Clear',
            'sku': 'PET-SH-2MM-CLR',
            'mpn': 'PETG2000C',
            'price_text': '$45.99',
            'specs_raw': {
                'material': 'PETG',
                'thickness': '2.0mm',
                'color': 'clear'
            },
            'specs_canonical': {
                'thickness_mm': 2.0,
                'color': 'clear'
            },
            'certifications': ['FDA approved', 'RoHS compliant'],
            'datasheet_url': 'https://example.com/datasheet.pdf',
            'source_url': 'https://example.com/product/123',
            'last_seen_at': '2024-01-15T10:00:00Z',
            'score': 25
        },
        {
            'product_id': 'test2',
            'supplier_id': 'supplier2',
            'name': 'PVC Gasket Round',
            'sku': 'PVC-GSK-RND', 
            'specs_raw': {
                'material': 'PVC',
                'shape': 'round'
            },
            'specs_canonical': {
                'diameter_mm': 50.0
            },
            'certifications': [],
            'source_url': 'https://example.com/product/456',
            'last_seen_at': '2024-01-16T10:00:00Z',
            'score': 12
        }
    ]
    
    print("\n1. Testing JSON save/load:")
    json_file = "data/test_products.json"
    
    # Save to JSON
    save_json(test_products, json_file)
    
    # Load from JSON
    loaded_products = load_json(json_file)
    print(f"  Loaded {len(loaded_products)} products from JSON")
    
    print("\n2. Testing CSV export:")
    csv_file = "data/test_products.csv"
    
    # Save to CSV
    save_products_csv(test_products, csv_file)
    
    print("\n3. Testing CSV import:")
    # Load from CSV
    csv_products = load_products_csv(csv_file)
    print(f"  Loaded {len(csv_products)} products from CSV")
    
    # Verify a product
    if csv_products:
        product = csv_products[0]
        print(f"  First product: {product['name']}")
        print(f"  Canonical specs: {len(product.get('specs_canonical', {}))}")
    
    print("\n4. Testing flattening:")
    flattened = flatten_product_for_csv(test_products[0])
    print(f"  Flattened product has {len(flattened)} fields:")
    for key, value in list(flattened.items())[:5]:  # Show first 5
        print(f"    {key}: {value}")
    
    print("\n5. Testing summary report:")
    report_file = "data/test_summary.json"
    create_summary_report(test_products, report_file)
    
    # Clean up test files
    import os
    for test_file in [json_file, csv_file, report_file]:
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"  Cleaned up: {test_file}")
    
    print("\n6. Store module testing complete!")