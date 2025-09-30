"""
Keywords module for expanding search terms with synonyms and relevant terms.
"""

import re
from typing import List, Set
try:
    import nltk
    from nltk.corpus import wordnet
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: NLTK not available. Install with: pip install nltk")

# Download required NLTK data if available
if NLTK_AVAILABLE:
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print("Downloading NLTK WordNet data...")
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)


def get_wordnet_synonyms(word: str, max_synonyms: int = 3) -> List[str]:
    """
    Get contextually relevant synonyms for a word using NLTK WordNet.

    Args:
        word: The word to find synonyms for
        max_synonyms: Maximum number of synonyms to return

    Returns:
        List of relevant synonyms
    """
    if not NLTK_AVAILABLE:
        return []

    # Filter out irrelevant synonyms for common industrial terms
    irrelevant_terms = {
        'plastic': {'credit card', 'charge card', 'charge plate'},
        'sheet': {'rag', 'mainsheet', 'tack', 'tabloid', 'piece of paper', 'sheet of paper'},
        'material': {'corporeal', 'substantial'},
        'industrial': {'heavy'},
    }

    synonyms = set()

    # Get synsets (synonym sets) for the word
    for syn in wordnet.synsets(word):
        # Focus on material/substance synsets for industrial terms
        if word.lower() in ['plastic', 'material', 'polymer']:
            if 'material' not in syn.definition() and 'substance' not in syn.definition():
                continue

        for lemma in syn.lemmas():
            synonym = lemma.name().replace('_', ' ')
            if (synonym.lower() != word.lower() and
                synonym.lower() not in irrelevant_terms.get(word.lower(), set())):
                synonyms.add(synonym.lower())

    return list(synonyms)[:max_synonyms]


def get_industrial_term_variants(term: str) -> List[str]:
    """
    Get common industrial variants for specialized terms.
    Uses a minimal fallback for highly technical terms not in WordNet.

    Args:
        term: The technical term

    Returns:
        List of variants
    """
    # Enhanced industrial mappings for better B2B matching
    critical_mappings = {
        # Plastics and polymers
        'plastic': ['polymer', 'resin', 'thermoplastic', 'material'],
        'petg': ['glycol-modified polyester', 'copolyester'],
        'ptfe': ['teflon', 'polytetrafluoroethylene'],
        'pom': ['delrin', 'acetal'],
        'peek': ['polyetheretherketone'],
        'pvc': ['vinyl', 'polyvinyl chloride'],
        'abs': ['acrylonitrile butadiene styrene'],
        'hdpe': ['high density polyethylene', 'polyethylene'],
        'pp': ['polypropylene'],
        'pc': ['polycarbonate'],
        'nylon': ['polyamide'],

        # Shapes and forms
        'sheet': ['plate', 'panel', 'board', 'stock'],
        'rod': ['bar', 'stick', 'round'],
        'tube': ['pipe', 'tubing', 'hollow'],
        'film': ['membrane', 'wrap'],

        # Industrial terms
        'gasket': ['seal', 'o-ring', 'washer'],
        'material': ['product', 'component', 'part'],
        'industrial': ['commercial', 'manufacturing'],

        # Standards and certifications
        'rohs': ['restriction of hazardous substances'],
        'reach': ['chemical regulation'],
        'iso': ['international standard'],
        'astm': ['american standard'],
        'fda': ['food grade', 'food safe'],
    }

    if term.lower() in critical_mappings:
        return critical_mappings[term.lower()]
    return []


def expand_keywords(query: str) -> List[str]:
    """
    Splits the user query and adds synonyms using NLTK WordNet to improve product-page recall.

    Args:
        query: The input search query string

    Returns:
        List of expanded terms including original words and synonyms
    """
    # Clean and split the query
    cleaned_query = re.sub(r'[^\w\s-]', ' ', query.lower())
    original_terms = cleaned_query.split()

    expanded_terms = set(original_terms)

    # Add synonyms for each term using WordNet
    for term in original_terms:
        # Skip very short terms or numbers
        if len(term) <= 2 or term.isdigit():
            continue

        # Get WordNet synonyms
        wordnet_synonyms = get_wordnet_synonyms(term, max_synonyms=3)
        expanded_terms.update(wordnet_synonyms)

        # Get industrial variants for technical terms
        industrial_variants = get_industrial_term_variants(term)
        expanded_terms.update(industrial_variants)

    return list(expanded_terms)


def extract_specifications(query: str) -> dict:
    """
    Extract numerical specifications and units from the query.
    
    Args:
        query: The input search query string
        
    Returns:
        Dictionary of extracted specifications
    """
    specs = {}
    
    # Common specification patterns
    patterns = {
        'thickness': r'(\d+(?:\.\d+)?)\s*(?:mm|mil|inch|in|")\s*(?:thick|thickness)',
        'width': r'(\d+(?:\.\d+)?)\s*(?:mm|cm|m|inch|in|")\s*(?:wide|width)',
        'length': r'(\d+(?:\.\d+)?)\s*(?:mm|cm|m|ft|foot|feet|inch|in|")\s*(?:long|length)',
        'diameter': r'(\d+(?:\.\d+)?)\s*(?:mm|cm|inch|in|")\s*(?:dia|diameter)',
        'temperature': r'(\d+(?:\.\d+)?)\s*(?:°?[cf]|celsius|fahrenheit)\s*(?:temp|temperature|max)',
        'pressure': r'(\d+(?:\.\d+)?)\s*(?:psi|bar|pa|mpa)\s*(?:pressure|max)',
        'durometer': r'(\d+(?:\.\d+)?)\s*(?:shore\s*[a-z]|durometer)',
    }
    
    query_lower = query.lower()
    
    for spec_type, pattern in patterns.items():
        matches = re.findall(pattern, query_lower, re.IGNORECASE)
        if matches:
            specs[spec_type] = matches[0]  # Take first match
            
    return specs


def get_industry_terms(query: str) -> List[str]:
    """
    Extract industry-specific terms and standards from the query.
    
    Args:
        query: The input search query string
        
    Returns:
        List of identified industry terms
    """
    industry_terms = []
    
    # Standards and certifications
    standards_patterns = [
        r'\b(iso\s*\d+)\b',
        r'\b(astm\s*[a-z]?\d+)\b', 
        r'\b(din\s*\d+)\b',
        r'\b(mil-\w+-\d+)\b',
        r'\b(usp\s*class\s*\w+)\b',
        r'\b(fda\s*approved?)\b',
        r'\b(rohs\s*compliant?)\b',
        r'\b(reach\s*compliant?)\b',
        r'\b(ce\s*mark(?:ed)?)\b',
    ]
    
    query_lower = query.lower()
    
    for pattern in standards_patterns:
        matches = re.findall(pattern, query_lower, re.IGNORECASE)
        industry_terms.extend(matches)
        
    # Industry applications
    applications = [
        'automotive', 'aerospace', 'medical', 'pharmaceutical', 'food',
        'electronics', 'electrical', 'marine', 'chemical', 'oil', 'gas',
        'semiconductor', 'solar', 'hvac', 'plumbing', 'construction'
    ]
    
    for app in applications:
        if app in query_lower:
            industry_terms.append(app)
            
    return list(set(industry_terms))  # Remove duplicates


if __name__ == "__main__":
    # Test the functions
    test_query = "PETG sheet 2mm ISO 9001 medical grade"
    
    print("Original query:", test_query)
    print("Expanded keywords:", expand_keywords(test_query))
    print("Extracted specs:", extract_specifications(test_query))
    print("Industry terms:", get_industry_terms(test_query))