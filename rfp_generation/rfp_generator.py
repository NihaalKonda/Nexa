from datetime import date
from jinja2 import Environment, FileSystemLoader
import os
import base64
from rfp_generation.prompts.rfp_prompts import rfp_prompt_templates
from rfp_generation.utils.gpt_client import generate_section
from rfp_generation.utils.pdf_utils import markdown_to_pdf_content


def generate_rfp_from_supplier(supplier_data: dict, search_data: dict, rfp_requirements: dict) -> dict:
    """
    Generate a complete RFP using supplier data, search context, and user requirements.

    Args:
        supplier_data: Supplier information from search results
        search_data: Original search parameters (product, location, price range)
        rfp_requirements: User-provided RFP details (title, timeline, standards, etc.)

    Returns:
        dict with 'markdown' and 'pdf_path' keys
    """

    # Build context for GPT prompts based on supplier and search data
    customer_data = build_customer_context(supplier_data, search_data, rfp_requirements)

    # Generate text sections using GPT-4
    sections = {}
    for key in ["Project", "Introduction", "ScopeOfWork", "Qualifications", "Timeline", "EvaluationCriteria", "PricingDetails"]:
        filled_prompt = rfp_prompt_templates[key].format(**customer_data)
        sections[key] = generate_section(filled_prompt)

    # Assemble context for Jinja2 template
    rfp_context = {
        "project_title": sections["Project"],
        "client_name": rfp_requirements.get("client_name", "Nexa"),
        "client_industry": search_data.get("product", "Procurement"),
        "rfp_date": date.today().strftime("%B %d, %Y"),
        "introduction": sections["Introduction"],
        "scope_of_work": sections["ScopeOfWork"],
        "qualifications": sections["Qualifications"],
        "timeline": sections["Timeline"],
        "timeline_data": customer_data["timeline_context"],
        "evaluation": sections["EvaluationCriteria"],
        "evaluation_weights": customer_data["evaluation_context"]["weights"],
        "non_negotiables": customer_data["evaluation_context"].get("non_negotiables", []),
        "pricing": sections["PricingDetails"],
        "pricing_data": customer_data["pricing_context"],
        "submission_deadline": rfp_requirements.get("submission_deadline", "TBD"),
        "submission_email_or_portal": rfp_requirements.get("submission_email", "procurement@nexa.org")
    }

    # Render Markdown using Jinja2 template
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("rfp_template.md.j2")
    rfp_markdown = template.render(rfp_context)

    # Generate PDF content in memory (no file saving)
    pdf_bytes = markdown_to_pdf_content(rfp_markdown)

    # Encode PDF to base64 for transmission
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

    # Generate filename for reference
    timestamp = date.today().strftime("%Y%m%d")
    supplier_name_clean = supplier_data.get("name", "unknown").replace(" ", "_").replace("/", "_")
    pdf_filename = f"rfp_{supplier_name_clean}_{timestamp}.pdf"

    return {
        "markdown": rfp_markdown,
        "pdf_content": pdf_base64,
        "pdf_filename": pdf_filename
    }


def build_customer_context(supplier_data: dict, search_data: dict, rfp_requirements: dict) -> dict:
    """Build the context dictionary for GPT prompts"""

    # Extract supplier and search information
    supplier_name = supplier_data.get("name", "Unknown Supplier")
    supplier_location = supplier_data.get("location", "N/A")
    product_title = supplier_data.get("product_title", search_data.get("product", "N/A"))
    price_range = supplier_data.get("price_range", "N/A")
    supplier_description = supplier_data.get("description", "")
    supplier_contact = supplier_data.get("contact", "")

    # Extract RFP form data
    client_name = rfp_requirements.get("client_name", "Nexa")
    delivery_location = rfp_requirements.get("location", search_data.get("location", "specified location"))
    delivery_date = rfp_requirements.get("deliveryDate", "TBD")
    budget = rfp_requirements.get("budget", price_range)
    project_description = rfp_requirements.get("projectDescription", "")
    standards = rfp_requirements.get("standards", "")
    additional_reqs = rfp_requirements.get("additionalRequirements", "")
    category = rfp_requirements.get("category", search_data.get("product", ""))

    # Build introduction context
    # Use project description if provided, otherwise use default text
    problem_statement = project_description if project_description else f"We require a reliable and qualified supplier for {product_title}. Our operations depend on consistent quality, timely delivery, and competitive pricing for this critical material/product."

    introduction_context = {
        "company": client_name,
        "industry": f"{category} services",
        "size": "Mid-sized enterprise",
        "problem": problem_statement,
        "goals": f"Establish a long-term strategic partnership with {supplier_name} to supply {product_title} to our {delivery_location} location. Target budget: {budget}. Expected delivery: {delivery_date}.",
        "history": f"We are currently evaluating {supplier_name} based on their expertise in {category}. {supplier_description if supplier_description else 'We seek a supplier with proven track record and industry certifications.'}"
    }

    # Build scope context
    scope_context = {
        "tasks": f"Vendor shall supply {product_title} from {supplier_name} ({supplier_location}). Price range: {price_range}. Delivery to {delivery_location} by {delivery_date}.",
        "tech_specs": f"Product must meet the following standards: {standards if standards else 'Industry-standard specifications and quality requirements'}. {additional_reqs}",
        "metrics": f"Key performance indicators: On-time delivery to {delivery_location}, quality compliance rate >98%, competitive pricing within {budget}, responsive customer service. Contact: {supplier_contact if supplier_contact != 'N/A' else 'To be provided'}.",
        "additional": additional_reqs if additional_reqs else f"Vendor must maintain consistent supply of {product_title} and provide regular quality reports."
    }

    # Build qualifications context
    standards_list = [s.strip() for s in standards.split(",")] if standards else []
    qualifications_context = {
        "experience": f"Vendor must demonstrate proven track record in supplying {product_title} or similar products. {supplier_name} claims expertise in {category}.",
        "certifications": standards_list if standards_list else ["ISO 9001 or equivalent quality management certification", "Industry-specific certifications as applicable"],
        "skills": [
            f"Expertise in manufacturing/distributing {product_title}",
            "Quality control and assurance processes",
            "Logistics and supply chain management",
            f"Ability to deliver to {delivery_location}",
            "Technical support and customer service"
        ]
    }

    # Build timeline context
    import datetime
    today = datetime.date.today()
    kickoff_date = (today + datetime.timedelta(days=7)).strftime("%B %d, %Y")
    final_date = delivery_date if delivery_date and delivery_date != "TBD" else (today + datetime.timedelta(days=90)).strftime("%B %d, %Y")

    timeline_context = {
        "kickoff": kickoff_date,
        "mvp": f"Initial delivery: {delivery_date if delivery_date and delivery_date != 'TBD' else 'Within 60 days'}",
        "testing": "Quality inspection and acceptance within 5 business days of delivery",
        "final": final_date
    }

    # Build evaluation context
    # Use custom evaluation criteria if provided, otherwise use defaults
    custom_eval_criteria = rfp_requirements.get("evaluationCriteria", {})
    additional_criteria = rfp_requirements.get("additionalCriteria", "")
    default_weights = {
        "technical_capability": 0.30,
        "pricing_competitiveness": 0.30,
        "delivery_reliability": 0.20,
        "quality_assurance": 0.15,
        "customer_service": 0.05
    }

    evaluation_context = {
        "weights": custom_eval_criteria if custom_eval_criteria else default_weights,
        "additional_notes": additional_criteria,
        "non_negotiables": [
            f"Must be able to deliver to {delivery_location}",
            f"Product must meet specification: {product_title}",
            f"Pricing must be competitive and within budget: {budget}"
        ]
    }

    if standards:
        evaluation_context["non_negotiables"].append(
            f"Must meet quality/certification standards: {standards}"
        )

    if additional_reqs:
        evaluation_context["non_negotiables"].append(
            f"Additional requirement: {additional_reqs[:100]}"  # First 100 chars
        )

    # Build pricing context
    pricing_context = {
        "currency": "USD",
        "format": "Detailed line-item breakdown with unit costs and quantities",
        "categories": [
            f"Unit price for {product_title}",
            f"Shipping and logistics to {delivery_location}",
            "Taxes and duties",
            "Quality inspection fees (if applicable)",
            "Rush delivery fees (if applicable)",
            "Volume discounts (if applicable)"
        ],
        "contract_length": rfp_requirements.get("contract_length") or "1 year",
        "budget_range": budget,
        "payment_terms": "Net 30 days from delivery and acceptance"
    }

    return {
        "introduction_context": introduction_context,
        "scope_context": scope_context,
        "qualifications_context": qualifications_context,
        "timeline_context": timeline_context,
        "evaluation_context": evaluation_context,
        "pricing_context": pricing_context
    }
