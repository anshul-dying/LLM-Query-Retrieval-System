# Multi-Format File Processing API

This API now supports processing multiple file formats for text extraction and analysis. The enhanced `DocumentProcessor` can handle various file types and extract meaningful text content from each.

## Supported File Types

### 1. **PDF Documents** (.pdf)
- Extracts text from all pages
- Handles multi-page documents
- Preserves text formatting and structure

### 2. **Word Documents** (.docx)
- Extracts text from paragraphs
- Handles document structure
- Supports rich text content

### 3. **PowerPoint Presentations** (.pptx, .ppt)
- Extracts text from all slides
- Handles slide titles and content
- Processes tables within slides
- Organizes content by slide number

### 4. **Excel Spreadsheets** (.xlsx, .xls)
- Extracts data from all worksheets
- Includes column headers
- Shows sample rows (first 10 rows)
- Provides summary statistics (row/column counts)
- Handles multiple sheets in a single file

### 5. **Images** (.jpg, .jpeg, .png, .bmp, .tiff, .gif)
- **OCR (Optical Character Recognition)** for text extraction
- Extracts image metadata (format, size, mode)
- Uses Tesseract OCR engine for high accuracy
- Supports various image formats

### 6. **ZIP Archives** (.zip)
- Lists all files in the archive
- Processes contained files based on their type
- Extracts text from PDFs, images, and text files within ZIP
- Provides file count and structure information

### 7. **Binary Files** (.bin)
- Analyzes file structure and metadata
- Detects file type using magic bytes
- Shows file size and hex preview
- Identifies common file formats (PNG, JPEG, PDF, ZIP)

## API Usage

### Endpoint
```
POST /api/v1/documents
```

### Request Body
```json
{
    "doc_url": "https://example.com/path/to/file.pptx"
}
```

### Response
```json
{
    "status": "success",
    "doc_id": "unique_document_id"
}
```

## Installation Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Additional System Requirements

For OCR functionality (image processing), you need to install Tesseract:

**Windows:**
```bash
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH environment variable
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

## Testing

Run the test script to verify file processing capabilities:

```bash
python scripts/test_file_processing.py
```

This will test processing with the sample URLs from your log file.

## Example Processing Results

### PowerPoint (.pptx)
```
--- Slide 1 ---
Title: Introduction
Content: Welcome to our presentation
Table: Column1 | Column2 | Column3

--- Slide 2 ---
Title: Key Points
Content: Important information here
```

### Excel (.xlsx)
```
--- Sheet: Sheet1 ---
Headers: Name | Age | Salary | Department
Row 1: John Doe | 30 | 50000 | Engineering
Row 2: Jane Smith | 25 | 45000 | Marketing
Summary: 100 rows, 4 columns
```

### Image (.jpeg)
```
Image Format: JPEG
Image Size: (1920, 1080)
Image Mode: RGB
--- OCR Text ---
Extracted text from the image using OCR...
```

### ZIP Archive
```
ZIP Archive Contents:
Total files: 5

--- File: document.pdf ---
Extracted PDF text content...

--- File: image.png ---
OCR Text: Text extracted from image...

--- File: data.xlsx ---
Excel data content...
```

## Error Handling

The API includes comprehensive error handling:
- Invalid file types return appropriate error messages
- Network errors are caught and reported
- File processing errors are logged with details
- Temporary files are automatically cleaned up

## Performance Considerations

- Large files are processed in chunks to manage memory
- Temporary files are automatically deleted after processing
- OCR processing may take longer for complex images
- ZIP files with many contained files may take additional time

## Security Features

- Files are downloaded to a temporary directory
- All temporary files are cleaned up after processing
- URL validation prevents malicious file access
- File size limits can be configured if needed 