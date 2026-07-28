import os
import logging
from typing import List, Dict, Any
from pypdf import PdfReader

logger = logging.getLogger(__name__)

class DocumentParser:
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """
        Extracts all text content from the file based on its file_type.
        Supports 'pdf', 'txt', 'log', and 'md'.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")

        file_type = file_type.lower().strip(".")
        
        if file_type == "pdf":
            logger.info(f"Extracting text from PDF: {file_path}")
            reader = PdfReader(file_path)
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            return "\n\n".join(pages_text)
        elif file_type in ("txt", "log", "md"):
            logger.info(f"Reading text file: {file_path}")
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type for parsing: {file_type}")

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Splits the input text into chunks of chunk_size with chunk_overlap.
        """
        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start forward
            if end >= text_len:
                break
            start += (chunk_size - chunk_overlap)

        return chunks
