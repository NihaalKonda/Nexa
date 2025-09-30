"""
Specifications normalization module for converting messy specifications to canonical format.
"""

import re
from typing import Dict, Optional, Tuple
from pint import UnitRegistry


# Initialize unit registry
ureg = UnitRegistry()


def create_normalization_map() -> Dict[str, str]:
    """
    Create a mapping of common specification labels to canonical keys.
    
    Returns:
        Dictionary mapping various label formats to canonical keys
    """
    return {
        # Dimensions
        'thickness': 'thickness_mm',
        'thick': 'thickness_mm',
        'gauge': 'thickness_mm',
        'depth': 'thickness_mm',
        'height': 'height_mm',
        'width': 'width_mm',
        'length': 'length_mm',
        'diameter': 'diameter_mm',
        'dia': 'diameter_mm',
        'radius': 'radius_mm',
        'size': 'size_mm',
        
        # Temperature
        'temperature': 'max_temp_c',
        'temp': 'max_temp_c',
        'max temperature': 'max_temp_c',
        'maximum temperature': 'max_temp_c',
        'max temp': 'max_temp_c',
        'operating temperature': 'operating_temp_c',
        'service temperature': 'service_temp_c',
        'melting temperature': 'melting_temp_c',
        'melting point': 'melting_temp_c',
        'glass transition': 'glass_transition_c',
        'tg': 'glass_transition_c',
        
        # Pressure
        'pressure': 'max_pressure_psi',
        'max pressure': 'max_pressure_psi',
        'working pressure': 'working_pressure_psi',
        'burst pressure': 'burst_pressure_psi',
        
        # Material Properties
        'density': 'density_g_cm3',
        'specific gravity': 'specific_gravity',
        'hardness': 'hardness_shore_a',
        'durometer': 'hardness_shore_a',
        'shore hardness': 'hardness_shore_a',
        'tensile strength': 'tensile_strength_psi',
        'elongation': 'elongation_percent',
        'modulus': 'modulus_psi',
        'compression set': 'compression_set_percent',
        
        # Electrical
        'dielectric strength': 'dielectric_strength_v_mil',
        'volume resistivity': 'volume_resistivity_ohm_cm',
        'surface resistivity': 'surface_resistivity_ohm',
        
        # Chemical
        'ph': 'ph',
        'ph range': 'ph',
        'chemical resistance': 'chemical_resistance',
        
        # Colors and Appearance
        'color': 'color',
        'colour': 'color',
        'transparency': 'transparency',
        'opacity': 'opacity',
        'finish': 'finish',
        'surface': 'surface_finish',
        
        # Standards and Certifications
        'standard': 'standard',
        'specification': 'specification',
        'grade': 'grade',
        'class': 'class',
        'type': 'type',
        
        # Manufacturing
        'tolerance': 'tolerance',
        'surface roughness': 'surface_roughness_ra',
        'flatness': 'flatness_mm',
    }


def normalize_units(value_str: str, target_unit: str) -> Optional[float]:
    """
    Convert a value string to the target unit using pint.
    
    Args:
        value_str: String containing value and unit (e.g., "2.5 inches", "80°F")
        target_unit: Target unit for conversion
        
    Returns:
        Normalized value as float, or None if conversion failed
    """
    if not value_str or not isinstance(value_str, str):
        return None
    
    # Clean the input string
    cleaned = value_str.strip()
    
    # Handle special cases first
    if target_unit.endswith('_c'):  # Temperature conversions
        temp_patterns = [
            (r'(\d+(?:\.\d+)?)\s*°?c(?:elsius)?', 'celsius'),
            (r'(\d+(?:\.\d+)?)\s*°?f(?:ahrenheit)?', 'fahrenheit'),
            (r'(\d+(?:\.\d+)?)\s*°?k(?:elvin)?', 'kelvin'),
        ]
        
        for pattern, unit in temp_patterns:
            match = re.search(pattern, cleaned.lower())
            if match:
                try:
                    quantity = ureg.Quantity(float(match.group(1)), unit)
                    return quantity.to('celsius').magnitude
                except:
                    pass
    
    # Length/dimension conversions to mm
    if target_unit.endswith('_mm'):
        length_patterns = [
            (r'(\d+(?:\.\d+)?)\s*mm', 'millimeter'),
            (r'(\d+(?:\.\d+)?)\s*cm', 'centimeter'),
            (r'(\d+(?:\.\d+)?)\s*m(?:\s|$)', 'meter'),
            (r'(\d+(?:\.\d+)?)\s*in(?:ch(?:es)?)?', 'inch'),
            (r'(\d+(?:\.\d+)?)\s*ft|(?:feet)', 'foot'),
            (r'(\d+(?:\.\d+)?)\s*mil', 'mil'),
        ]
        
        for pattern, unit in length_patterns:
            match = re.search(pattern, cleaned.lower())
            if match:
                try:
                    quantity = ureg.Quantity(float(match.group(1)), unit)
                    return quantity.to('millimeter').magnitude
                except:
                    pass
    
    # Pressure conversions to PSI
    if target_unit.endswith('_psi'):
        pressure_patterns = [
            (r'(\d+(?:\.\d+)?)\s*psi', 'psi'),
            (r'(\d+(?:\.\d+)?)\s*bar', 'bar'),
            (r'(\d+(?:\.\d+)?)\s*pa', 'pascal'),
            (r'(\d+(?:\.\d+)?)\s*mpa', 'megapascal'),
            (r'(\d+(?:\.\d+)?)\s*kpa', 'kilopascal'),
        ]
        
        for pattern, unit in pressure_patterns:
            match = re.search(pattern, cleaned.lower())
            if match:
                try:
                    quantity = ureg.Quantity(float(match.group(1)), unit)
                    return quantity.to('psi').magnitude
                except:
                    pass
    
    # For density (g/cm³)
    if target_unit == 'density_g_cm3':
        density_patterns = [
            (r'(\d+(?:\.\d+)?)\s*g/cm[³3]', 'gram/centimeter**3'),
            (r'(\d+(?:\.\d+)?)\s*kg/m[³3]', 'kilogram/meter**3'),
        ]
        
        for pattern, unit in density_patterns:
            match = re.search(pattern, cleaned.lower())
            if match:
                try:
                    quantity = ureg.Quantity(float(match.group(1)), unit)
                    return quantity.to('gram/centimeter**3').magnitude
                except:
                    pass
    
    # For percentages (just extract number)
    if target_unit.endswith('_percent'):
        percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%?', cleaned)
        if percent_match:
            try:
                return float(percent_match.group(1))
            except:
                pass
    
    # For dimensionless numbers (Shore hardness, pH, etc.)
    if target_unit in ['hardness_shore_a', 'ph', 'specific_gravity']:
        # Look for numbers, possibly with descriptive text
        number_match = re.search(r'(\d+(?:\.\d+)?)', cleaned)
        if number_match:
            try:
                return float(number_match.group(1))
            except:
                pass
    
    # Generic number extraction for other cases
    number_match = re.search(r'(\d+(?:\.\d+)?)', cleaned)
    if number_match:
        try:
            return float(number_match.group(1))
        except:
            pass
    
    return None


def normalize_label(label: str) -> Optional[str]:
    """
    Normalize a specification label to canonical format.
    
    Args:
        label: Raw specification label
        
    Returns:
        Canonical label or None if not recognized
    """
    if not label or not isinstance(label, str):
        return None
    
    # Clean the label
    cleaned = label.lower().strip()
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned)  # Remove punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned)      # Normalize spaces
    cleaned = cleaned.strip()
    
    # Get normalization map
    norm_map = create_normalization_map()
    
    # Direct match
    if cleaned in norm_map:
        return norm_map[cleaned]
    
    # Partial matches
    for key, canonical in norm_map.items():
        if key in cleaned or cleaned in key:
            return canonical
    
    # Special handling for complex labels
    if any(word in cleaned for word in ['thick', 'gauge', 'depth']) and any(word in cleaned for word in ['mm', 'mil', 'inch']):
        return 'thickness_mm'
    
    if any(word in cleaned for word in ['temp', 'temperature']) and any(word in cleaned for word in ['max', 'maximum']):
        return 'max_temp_c'
    
    if any(word in cleaned for word in ['width', 'wide']) and any(word in cleaned for word in ['mm', 'cm', 'inch']):
        return 'width_mm'
    
    if any(word in cleaned for word in ['length', 'long']) and any(word in cleaned for word in ['mm', 'cm', 'inch']):
        return 'length_mm'
    
    return None


def normalize_specifications(specs_raw: Dict[str, str]) -> Dict[str, any]:
    """
    Normalize raw specifications to canonical format.
    
    Args:
        specs_raw: Raw specifications dictionary
        
    Returns:
        Dictionary with canonical keys and normalized values
    """
    if not specs_raw or not isinstance(specs_raw, dict):
        return {}
    
    normalized = {}
    
    for raw_label, raw_value in specs_raw.items():
        if not raw_label or not raw_value:
            continue
        
        # Normalize the label
        canonical_label = normalize_label(raw_label)
        if not canonical_label:
            continue
        
        # Determine target unit from canonical label
        target_unit = canonical_label
        
        # Try to normalize the value
        normalized_value = normalize_units(str(raw_value), target_unit)
        
        if normalized_value is not None:
            normalized[canonical_label] = normalized_value
        else:
            # If numeric normalization fails, keep as string but with canonical label
            normalized[canonical_label] = str(raw_value)
    
    return normalized


def get_specification_info(canonical_key: str) -> Dict[str, str]:
    """
    Get information about a canonical specification key.
    
    Args:
        canonical_key: Canonical specification key
        
    Returns:
        Dictionary with key information
    """
    info_map = {
        'thickness_mm': {'unit': 'mm', 'type': 'dimension', 'description': 'Material thickness'},
        'width_mm': {'unit': 'mm', 'type': 'dimension', 'description': 'Material width'},
        'length_mm': {'unit': 'mm', 'type': 'dimension', 'description': 'Material length'},
        'height_mm': {'unit': 'mm', 'type': 'dimension', 'description': 'Material height'},
        'diameter_mm': {'unit': 'mm', 'type': 'dimension', 'description': 'Material diameter'},
        'max_temp_c': {'unit': '°C', 'type': 'temperature', 'description': 'Maximum operating temperature'},
        'operating_temp_c': {'unit': '°C', 'type': 'temperature', 'description': 'Operating temperature'},
        'max_pressure_psi': {'unit': 'PSI', 'type': 'pressure', 'description': 'Maximum pressure rating'},
        'density_g_cm3': {'unit': 'g/cm³', 'type': 'physical', 'description': 'Material density'},
        'hardness_shore_a': {'unit': 'Shore A', 'type': 'mechanical', 'description': 'Shore A hardness'},
        'tensile_strength_psi': {'unit': 'PSI', 'type': 'mechanical', 'description': 'Tensile strength'},
        'elongation_percent': {'unit': '%', 'type': 'mechanical', 'description': 'Elongation at break'},
        'color': {'unit': None, 'type': 'appearance', 'description': 'Material color'},
        'grade': {'unit': None, 'type': 'classification', 'description': 'Material grade'},
        'standard': {'unit': None, 'type': 'certification', 'description': 'Applicable standard'},
    }
    
    return info_map.get(canonical_key, {
        'unit': None,
        'type': 'other',
        'description': 'Specification'
    })


if __name__ == "__main__":
    # Test the normalization functions
    print("=" * 60)
    print("TESTING SPECIFICATIONS NORMALIZATION MODULE")
    print("=" * 60)
    
    print("\n1. Testing label normalization:")
    test_labels = [
        "Thickness (mm)",
        "Width",
        "Max Temperature",
        "Shore Hardness",
        "Tensile Strength (psi)",
        "Color/Colour",
        "Density g/cm³"
    ]
    
    for label in test_labels:
        canonical = normalize_label(label)
        print(f"  '{label}' -> '{canonical}'")
    
    print("\n2. Testing unit normalization:")
    test_values = [
        ("2.5 mm", "thickness_mm"),
        ("0.1 inches", "thickness_mm"),
        ("80°F", "max_temp_c"),
        ("150 PSI", "max_pressure_psi"),
        ("50 Shore A", "hardness_shore_a"),
        ("95%", "elongation_percent"),
    ]
    
    for value, target in test_values:
        normalized = normalize_units(value, target)
        print(f"  '{value}' -> {normalized} ({target})")
    
    print("\n3. Testing full specification normalization:")
    test_specs = {
        "Thickness (mm)": "2.5",
        "Width": "100 mm",
        "Max Temp": "80°C",
        "Color": "Clear",
        "Shore Hardness": "70A",
        "Working Pressure": "150 PSI",
        "Density": "1.27 g/cm³"
    }
    
    normalized_specs = normalize_specifications(test_specs)
    print("  Raw specifications:")
    for key, value in test_specs.items():
        print(f"    {key}: {value}")
    
    print("  Normalized specifications:")
    for key, value in normalized_specs.items():
        info = get_specification_info(key)
        unit_str = f" {info['unit']}" if info['unit'] else ""
        print(f"    {key}: {value}{unit_str} ({info['description']})")
    
    print("\n4. Testing specification info:")
    for canonical_key in ['thickness_mm', 'max_temp_c', 'color']:
        info = get_specification_info(canonical_key)
        print(f"  {canonical_key}: {info}")