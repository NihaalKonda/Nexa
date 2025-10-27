import markdown
from xhtml2pdf import pisa
from io import BytesIO

def markdown_to_pdf_content(markdown_text: str):
    """
    Convert markdown to PDF content (in memory, no file saving).
    Returns PDF as bytes.
    """
    try:
        # Convert markdown to HTML first
        html_content = markdown.markdown(
            markdown_text,
            extensions=['tables', 'fenced_code', 'nl2br']
        )

        # Add beautiful styling for PDF
        styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>RFP Document</title>
    <style>
        @page {{
            size: letter;
            margin: 20mm;
        }}

        body {{
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12pt;
            line-height: 1.8;
            color: #333;
            background: white;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }}

        h1 {{
            font-size: 32px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            color: #2c3e50;
        }}

        h2 {{
            font-size: 24px;
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 8px;
            color: #34495e;
        }}

        h3 {{
            font-size: 20px;
            color: #7f8c8d;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}

        th {{
            background-color: #3498db;
            color: white;
            font-weight: 600;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        code {{
            background-color: #f6f8fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #e74c3c;
        }}

        pre {{
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }}

        ul, ol {{
            padding-left: 24px;
        }}

        li {{
            margin: 8px 0;
        }}

        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 32px 0;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""

        # Generate PDF to in-memory buffer
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(
            styled_html,
            dest=pdf_buffer
        )

        if pisa_status.err:
            raise Exception(f"PDF generation had errors")

        # Get PDF bytes
        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()

        return pdf_bytes

    except Exception as e:
        print(f"PDF generation error: {e}")
        raise Exception(f"Failed to generate PDF: {e}")