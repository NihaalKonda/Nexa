rfp_prompt_templates = {
    "Project": (
        "Generate ONLY a concise, specific project title for this RFP. Do not add explanations or examples.\n\n"
        "Context:\n{introduction_context}\n\n"
        "Format: 'RFP for [Product/Service] Supply from [Supplier] to [Client]'\n\n"
        "Example output: 'RFP for Aluminum Sheet Supply from Metals USA to Nexa'\n\n"
        "Return only the title, nothing else."
    ),

    "Introduction": (
        "Write the Introduction section of an RFP. "
        "Include:\n"
        "- A short overview of the client company (industry, size, operations).\n"
        "- The business problem or need they are addressing.\n"
        "- Their strategic goals and desired outcomes.\n"
        "Use the following data to ground the response:\n\n{introduction_context}\n\n"
        "Keep the tone professional and clear."
    ),

    "ScopeOfWork": (
        "Write the Scope of Work section of an RFP. "
        "Describe what the vendor is expected to deliver.\n"
        "Include:\n"
        "- Specific tasks and deliverables.\n"
        "- Technical specifications or required standards.\n"
        "- Quantifiable performance metrics.\n"
        "- Any services needed beyond delivery (e.g., support, training).\n\n"
        "Use the following structured data:\n\n{scope_context}\n\n"
        "Keep it precise and implementation-oriented."
    ),

    "Qualifications": (
        "Write the Qualifications section of an RFP. "
        "List the minimum qualifications vendors must meet.\n"
        "Include:\n"
        "- Required experience or certifications.\n"
        "- Relevant past projects or case studies.\n"
        "- Required team skills or domain expertise.\n"
        "- Compliance or regulatory requirements.\n\n"
        "Use this data:\n\n{qualifications_context}\n\n"
        "Format it in clear, complete sentences."
    ),

    "Timeline": (
        "Write the Timeline section of an RFP. "
        "Include:\n"
        "- Project start and end dates.\n"
        "- Key milestones and review points.\n"
        "- Testing or integration phases.\n"
        "- Any flexibility or constraints.\n\n"
        "Use this timeline data:\n\n{timeline_context}\n\n"
        "Present it clearly and logically."
    ),

    "EvaluationCriteria": (
        "Write the Evaluation Criteria section of an RFP. "
        "Describe how proposals will be scored.\n"
        "Include:\n"
        "- Explanation of the weighted evaluation criteria (e.g., technical, price, experience).\n"
        "- Any required vs. optional capabilities.\n"
        "- Qualitative factors that will be considered.\n"
        "- If additional notes are provided in the context, incorporate them into your explanation.\n\n"
        "Note: Do NOT list the non-negotiables, as they will be added separately in the template.\n\n"
        "Use the following structured data:\n\n{evaluation_context}\n\n"
        "Keep the tone formal and unambiguous."
    ),

    "PricingDetails": (
        "Write the Pricing Details section of an RFP. "
        "Explain how vendors should structure their pricing.\n"
        "Include:\n"
        "- Required pricing format and currency.\n"
        "- Contract length expectations.\n"
        "- Required cost categories (e.g., setup, licensing).\n"
        "- Any performance-based or volume discount expectations.\n\n"
        "Use this pricing data:\n\n{pricing_context}\n\n"
        "Make it clear and standardized."
    )
}
