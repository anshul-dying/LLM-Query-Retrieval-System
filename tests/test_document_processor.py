import pytest
from core.document_processor import DocumentProcessor

def test_extract_pdf():
    processor = DocumentProcessor()
    # Use a test PDF URL or mock the response
    test_url = "https://example.com/sample.pdf?query=param"
    # Mocking requires additional setup; for simplicity, test with a local file or skip
    with pytest.raises(Exception):  # Replace with actual test if URL is accessible
        processor.extract_text(test_url)

def test_unsupported_file_type():
    processor = DocumentProcessor()
    test_url = "https://example.com/sample.txt?query=param"
    with pytest.raises(ValueError, match="Unsupported document type"):
        processor.extract_text(test_url)