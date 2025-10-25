import pypandoc

def markdown_to_pdf(markdown_text: str, output_path: str):
    pypandoc.convert_text(
        markdown_text,
        'pdf',
        format='md',
        outputfile=output_path,
        extra_args=['--standalone']
    )
    return output_path
