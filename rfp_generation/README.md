# RFP Generation Module

This module generates professional Request for Proposals (RFPs) using GPT-4, Jinja2 templates, and exports them as PDF documents.

## Features

- **GPT-4 Powered**: Each section of the RFP is generated using GPT-4 with specialized prompts
- **Template-Based**: Uses Jinja2 templates for consistent formatting
- **PDF Export**: Automatically converts markdown to PDF using pypandoc
- **Supplier Integration**: Pulls data from supplier search results to pre-populate RFP details

## Directory Structure

```
rfp_generation/
├── __init__.py
├── rfp_generator.py          # Main RFP generation logic
├── prompts/
│   ├── __init__.py
│   └── rfp_prompts.py         # GPT prompt templates for each section
├── templates/
│   └── rfp_template.md.j2     # Jinja2 markdown template
└── utils/
    ├── __init__.py
    ├── gpt_client.py          # OpenAI API client
    └── pdf_utils.py           # PDF conversion utilities
```

## How It Works

### 1. Data Input
The system takes three types of input:
- **Supplier Data**: Information about the selected supplier (name, location, product, price, etc.)
- **Search Data**: Original search parameters (product, location, price range)
- **RFP Requirements**: User-provided details (title, timeline, standards, budget, etc.)

### 2. Context Building
The `build_customer_context()` function transforms the input data into structured contexts for each RFP section:
- Introduction Context
- Scope of Work Context
- Qualifications Context
- Timeline Context
- Evaluation Criteria Context
- Pricing Details Context

### 3. GPT-4 Generation
Each section uses a specialized prompt template from `rfp_prompts.py`:
- **Project**: Generates a concise title
- **Introduction**: Company overview, problem statement, goals
- **ScopeOfWork**: Tasks, deliverables, technical specs
- **Qualifications**: Required experience, certifications, skills
- **Timeline**: Project dates, milestones, phases
- **EvaluationCriteria**: Scoring weights, non-negotiables
- **PricingDetails**: Pricing format, categories, contract terms

### 4. Template Rendering
The generated sections are passed to the Jinja2 template (`rfp_template.md.j2`), which assembles them into a complete markdown document with:
- Project overview header
- All sections with proper formatting
- Tables for timeline and evaluation criteria
- Submission instructions

### 5. PDF Export
The markdown document is converted to PDF using `pypandoc` and saved to `data/rfp_outputs/`.

## API Usage

### Generate RFP Endpoint

**POST** `/api/rfp/generate`

```json
{
  "supplier": {
    "name": "Industrial Supply Co.",
    "location": "Buffalo, NY",
    "product_title": "Aluminum Sheets 4x8",
    "price_range": "$85 per sheet",
    "description": "...",
    "website": "...",
    "contact": "..."
  },
  "search_data": {
    "product": "aluminum sheets",
    "location": "Buffalo, NY",
    "priceMin": "50",
    "priceMax": "300"
  },
  "rfp_requirements": {
    "title": "RFP for Aluminum Sheet Supply",
    "category": "Industrial Materials",
    "location": "Buffalo, NY",
    "deliveryDate": "2026-06-01",
    "budget": "$50,000 - $100,000",
    "standards": "ISO 9001, ASTM B209",
    "additionalRequirements": "Must support rush orders",
    "client_name": "Nexa",
    "submission_deadline": "December 15, 2025",
    "submission_email": "procurement@nexa.org",
    "contract_length": "1 year"
  }
}
```

**Response:**
```json
{
  "success": true,
  "markdown": "# Request for Proposal (RFP)...",
  "pdf_filename": "rfp_Industrial_Supply_Co._20251017.pdf",
  "pdf_path": "/path/to/data/rfp_outputs/rfp_Industrial_Supply_Co._20251017.pdf"
}
```

### Download PDF Endpoint

**GET** `/api/rfp/download/<filename>`

Downloads the generated PDF file.

## Frontend Integration

### Search Results Page
Each supplier card has a "Generate RFP" button that:
1. Encodes supplier data in URL parameters
2. Navigates to `/rfp/generate?supplier=...&product=...`

### RFP Generation Page (`/rfp/generate`)
1. Pre-fills form with supplier and search data
2. User adds additional requirements (timeline, standards, etc.)
3. Calls Flask backend `/api/rfp/generate`
4. Displays markdown preview
5. Allows downloading PDF or copying markdown

## Dependencies

Required Python packages (see `requirements.txt`):
- `Jinja2>=3.1.0` - Template rendering
- `pypandoc>=1.11` - Markdown to PDF conversion
- `openai>=1.12.0` - GPT-4 API access

**Note**: pypandoc requires pandoc to be installed on the system:
```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc

# Or use conda
conda install -c conda-forge pandoc
```

## Example Output

The generated RFP includes:
- Professional header with project details
- Introduction with company background and goals
- Detailed scope of work
- Vendor qualification requirements
- Project timeline with milestone table
- Evaluation criteria with weighted scoring
- Pricing guidelines
- Submission instructions

## Customization

### Modifying Prompts
Edit `prompts/rfp_prompts.py` to change how GPT generates each section.

### Changing Template
Edit `templates/rfp_template.md.j2` to modify the layout and formatting.

### PDF Styling
pypandoc supports various PDF options. Modify `utils/pdf_utils.py` to add custom styling:
```python
pypandoc.convert_text(
    markdown_text,
    'pdf',
    format='md',
    outputfile=output_path,
    extra_args=[
        '--standalone',
        '--pdf-engine=xelatex',  # Different PDF engine
        '-V', 'geometry:margin=1in',  # Custom margins
        '--toc',  # Table of contents
    ]
)
```

## Troubleshooting

### PDF Generation Fails
- Ensure pandoc is installed: `pandoc --version`
- Check pypandoc installation: `pip show pypandoc`
- Verify output directory exists and is writable

### GPT Generation Errors
- Check OpenAI API key in `.env`
- Verify API usage limits
- Check prompt length (max tokens)

### Template Rendering Issues
- Validate Jinja2 syntax in template
- Check that all required variables are provided
- Use try-except blocks for missing fields
