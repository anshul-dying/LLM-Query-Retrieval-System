#!/usr/bin/env python3
"""
Test script for multi-format file processing
Tests the DocumentProcessor with various file types
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.document_processor import DocumentProcessor
from loguru import logger

def test_file_processing():
    """Test the document processor with different file types"""
    
    # Test URLs from your log file
    test_urls = [
        "https://hackrx.blob.core.windows.net/assets/Test%20/image.jpeg?sv=2023-01-03&spr=https&st=2025-08-04T19%3A29%3A01Z&se=2026-08-05T19%3A29%3A00Z&sr=b&sp=r&sig=YnJJThygjCT6%2FpNtY1aHJEZ%2F%2BqHoEB59TRGPSxJJBwo%3D",
        "https://hackrx.blob.core.windows.net/assets/Test%20/Pincode%20data.xlsx?sv=2023-01-03&spr=https&st=2025-08-04T18%3A50%3A43Z&se=2026-08-05T18%3A50%3A00Z&sr=b&sp=r&sig=xf95kP3RtMtkirtUMFZn%2FFNai6sWHarZsTcvx8ka9mI%3D",
        "https://hackrx.blob.core.windows.net/assets/Test%20/Salary%20data.xlsx?sv=2023-01-03&spr=https&st=2025-08-04T18%3A46%3A54Z&se=2026-08-05T18%3A46%3A00Z&sr=b&sp=r&sig=sSoLGNgznoeLpZv%2FEe%2FEI1erhD0OQVoNJFDPtqfSdJQ%3D",
        "https://hackrx.blob.core.windows.net/assets/Test%20/Test%20Case%20HackRx.pptx?sv=2023-01-03&spr=https&st=2025-08-04T18%3A36%3A56Z&se=2026-08-05T18%3A36%3A00Z&sr=b&sp=r&sig=v3zSJ%2FKW4RhXaNNVTU9KQbX%2Bmo5dDEIzwaBzXCOicJM%3D",
        "https://hackrx.blob.core.windows.net/assets/hackrx_pdf.zip?sv=2023-01-03&spr=https&st=2025-08-04T09%3A25%3A45Z&se=2027-08-05T09%3A25%3A00Z&sr=b&sp=r&sig=rDL2ZcGX6XoDga5%2FTwMGBO9MgLOhZS8PUjvtga2cfVk%3D",
        "https://ash-speed.hetzner.com/10GB.bin"
    ]
    
    processor = DocumentProcessor()
    
    for i, url in enumerate(test_urls, 1):
        try:
            logger.info(f"Testing file {i}: {url}")
            
            # Extract filename for display
            filename = url.split("/")[-1].split("?")[0]
            logger.info(f"Processing: {filename}")
            
            # Process the file
            text = processor.extract_text(url)
            
            # Show summary
            logger.success(f"Successfully processed {filename}")
            logger.info(f"Extracted {len(text)} characters")
            logger.info(f"Preview: {text[:200]}...")
            
        except Exception as e:
            logger.error(f"Failed to process {url}: {str(e)}")
        
        print("-" * 80)

if __name__ == "__main__":
    logger.info("Starting file processing tests...")
    test_file_processing()
    logger.info("File processing tests completed!") 