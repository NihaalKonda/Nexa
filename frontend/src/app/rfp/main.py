from datetime import date
from jinja2 import Environment, FileSystemLoader

from prompts.rfp_prompts import rfp_prompt_templates
from utils.gpt_client import generate_section
from utils.pdf_utils import markdown_to_pdf

# Example client data
customer_data = {
    "introduction_context": {
        "company": "Nexa",
        "industry": "Procurement Automation",
        "size": "Mid-sized",
        "problem": "Manual sourcing is slow",
        "goals": "Reduce procurement time by 40% by Q2 2026",
        "history": "Using spreadsheets for vendor management"
    },
    "scope_context": {
        "tasks": "Develop supplier discovery + RFP automation modules",
        "tech_specs": "Integrate with SAP and Postgres",
        "integrations": ["SAP", "NetSuite"],
        "metrics": "Index 100K+ suppliers, 99.9% uptime"
    },
    "qualifications_context": {
        "experience": "3+ enterprise deployments",
        "certifications": ["SOC 2 Type II"],
        "skills": ["NLP", "full-stack", "procurement domain"]
    },
    "timeline_context": {
        "start": "Jan 2026",
        "mvp": "Apr 2026",
        "testing": "6 weeks",
        "final": "Jun 2026"
    },
    "evaluation_context": {
        "weights": {"technical": 0.4, "price": 0.3, "experience": 0.2, "timeline": 0.1},
        "non_negotiables": ["Must host in US", "SSO required"]
    },
    "pricing_context": {
        "currency": "USD",
        "format": "line-item breakdown",
        "categories": ["setup", "licensing", "support", "training"],
        "contract_length": "3 years"
    }
}

# Generate text sections
sections = {}
for key in ["Project", "Introduction", "ScopeOfWork", "Qualifications", "Timeline", "EvaluationCriteria", "PricingDetails"]:
    filled_prompt = rfp_prompt_templates[key].format(**customer_data)
    sections[key] = generate_section(filled_prompt)

# Assemble context for Jinja2
rfp_context = {
    "project_title": sections["Project"],
    "client_name": customer_data["introduction_context"]["company"],
    "client_industry": customer_data["introduction_context"]["industry"],
    "rfp_date": date.today().strftime("%B %d, %Y"),
    "introduction": sections["Introduction"],
    "scope_of_work": sections["ScopeOfWork"],
    "qualifications": sections["Qualifications"],
    "timeline": sections["Timeline"],
    "timeline_data": {
        "kickoff": "Jan 2026",
        "mvp": "Apr 2026",
        "testing": "6 weeks",
        "final": "Jun 2026"
    },
    "evaluation": sections["EvaluationCriteria"],
    "evaluation_weights": customer_data["evaluation_context"]["weights"],
    "non_negotiables": customer_data["evaluation_context"]["non_negotiables"],
    "pricing": sections["PricingDetails"],
    "pricing_data": customer_data["pricing_context"],
    "submission_deadline": "December 15, 2025",
    "submission_email_or_portal": "procurement@nexa.org"
}

# Render Markdown
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("rfp_template.md.j2")
rfp_markdown = template.render(rfp_context)

# Export PDF
output_file = markdown_to_pdf(rfp_markdown, "rfp_output.pdf")
print(f"✅ RFP generated: {output_file}")
