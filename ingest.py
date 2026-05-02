import requests
from lxml import etree
import uuid
import os
from config import MIN_PARAGRAPH_LENGTH

GROBID_URL = "http://localhost:8070/api/processFulltextDocument"


def parse_pdf(pdf_path):
    """
    Takes a research paper PDF and returns structured paragraphs.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        List of dictionaries with structure:
        [
          {
            "section": "...",
            "paragraph_id": "...",
            "text": "...",
            "citations": [...]
          }
        ]
    
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        RuntimeError: If GROBID processing fails
        ValueError: If PDF cannot be parsed
    """
    
    # Validate file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Validate file is a PDF
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError(f"File must be a PDF: {pdf_path}")
    
    try:
        # Send to GROBID
        with open(pdf_path, "rb") as f:
            response = requests.post(
                GROBID_URL,
                files={"input": f},
                timeout=120  # 2 minute timeout
            )

        if response.status_code != 200:
            error_msg = f"GROBID processing failed with status {response.status_code}"
            if response.status_code == 503:
                error_msg += " (GROBID server may not be running)"
            raise RuntimeError(error_msg)

        # Parse XML response
        return grobid_xml_to_paragraphs(response.text)
        
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to GROBID server. "
            "Ensure GROBID is running at http://localhost:8070"
        )
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "GROBID processing timed out. "
            "The PDF might be too large or complex."
        )
    except Exception as e:
        raise RuntimeError(f"Error processing PDF: {str(e)}")


def grobid_xml_to_paragraphs(xml_text):
    """
    Convert GROBID XML output to structured paragraphs.
    
    Args:
        xml_text: XML string from GROBID
    
    Returns:
        List of paragraph dictionaries
    
    Raises:
        ValueError: If XML cannot be parsed
    """
    
    try:
        root = etree.XML(xml_text.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        raise ValueError(f"Invalid XML from GROBID: {str(e)}")
    
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    results = []

    # Extract paragraphs from document structure
    for div in root.xpath("//tei:div", namespaces=ns):
        # Get section title
        section_title = div.xpath(".//tei:head/text()", namespaces=ns)
        section_name = section_title[0].strip() if section_title else "Unknown"

        # Get all paragraphs in this section
        paragraphs = div.xpath(".//tei:p", namespaces=ns)

        for p in paragraphs:
            # Extract all text from paragraph
            text = " ".join(p.xpath(".//text()")).strip()
            
            # Skip short paragraphs (likely noise)
            if len(text) < MIN_PARAGRAPH_LENGTH:
                continue

            # Extract citations
            citations = p.xpath(".//tei:ref[@type='bibr']/text()", namespaces=ns)
            citations = [c.strip() for c in citations if c.strip()]

            results.append({
                "section": section_name,
                "paragraph_id": str(uuid.uuid4())[:8],
                "text": text,
                "citations": citations
            })

    if not results:
        raise ValueError(
            "No valid paragraphs extracted from PDF. "
            "The PDF might be empty, corrupted, or not text-based."
        )

    return results


def parse_text_directly(text, section_name="Main"):
    """
    Parse plain text directly without GROBID.
    Useful for testing or when GROBID is not available.
    
    Args:
        text: Plain text string
        section_name: Name for the section
    
    Returns:
        List of paragraph dictionaries
    """
    
    # Split into paragraphs (by double newline or single newline)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # If no double newlines, split by single newline
    if len(paragraphs) <= 1:
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    results = []
    
    for para_text in paragraphs:
        if len(para_text) < MIN_PARAGRAPH_LENGTH:
            continue
        
        results.append({
            "section": section_name,
            "paragraph_id": str(uuid.uuid4())[:8],
            "text": para_text,
            "citations": []  # Cannot extract citations from plain text
        })
    
    return results
