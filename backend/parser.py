import pdfplumber
from docx import Document
from io import BytesIO

def extract_text(content:bytes, filename: str) -> str:
    """Extracts raw text from PDF or DOCX files."""
    if filename.endswith('.pdf'):
        with pdfplumber.open(BytesIO(content)) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        
    elif filename.endswith('.docx'):
        doc = Document(BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs])
    
    return ""