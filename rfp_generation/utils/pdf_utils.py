import markdown

def markdown_to_pdf(markdown_text: str, output_path: str):
    """
    Convert markdown to a styled HTML file (PDF generation simplified for now).
    User can print to PDF from their browser.
    """
    try:
        # Convert markdown to HTML first
        html_content = markdown.markdown(
            markdown_text,
            extensions=['tables', 'fenced_code', 'nl2br']
        )

        # Add beautiful styling and print-ready CSS
        styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>RFP Document</title>
    <style>
        @media print {{
            body {{
                margin: 0;
                padding: 20mm;
            }}
            .no-print {{
                display: none;
            }}
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: white;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            page-break-after: avoid;
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
            page-break-inside: avoid;
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
        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            z-index: 1000;
        }}
        .print-button:hover {{
            background: #2980b9;
        }}
        @page {{
            size: letter;
            margin: 20mm;
        }}
    </style>
</head>
<body>
    <button class="print-button no-print" onclick="window.print()">Print/Save as PDF</button>
    {html_content}
</body>
</html>"""

        # Save as HTML (user can print to PDF from browser)
        html_path = output_path.replace('.pdf', '.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(styled_html)

        return html_path

    except Exception as e:
        print(f"HTML generation error: {e}")
        raise Exception(f"Failed to generate HTML: {e}")
