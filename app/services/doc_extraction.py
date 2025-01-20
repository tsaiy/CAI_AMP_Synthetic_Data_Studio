import fitz
import docx
from pathlib import Path
import re
from typing import List, Optional

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        """
        Initialize DocumentProcessor with chunking parameters.
        
        Args:
            chunk_size (int): Maximum size of each chunk in characters
            overlap (int): Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.supported_formats = {'.pdf', '.doc', '.docx', '.txt'}

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text (str): Input text to be chunked
            
        Returns:
            List[str]: List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end < len(text):
                break_point = text.rfind('.', start, end)
                if break_point == -1:
                    break_point = text.rfind(' ', start, end)
                if break_point != -1:
                    end = break_point + 1
            
            chunks.append(text[start:end].strip())
            start = end - self.overlap
            
        return [chunk for chunk in chunks if chunk]

    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        with fitz.open(file_path) as doc:
            return " ".join(page.get_text() for page in doc)

    def _extract_doc(self, file_path: Path) -> str:
        """Extract text from DOC/DOCX file."""
        doc = docx.Document(file_path)
        return ' '.join(paragraph.text for paragraph in doc.paragraphs)

    def _extract_txt(self, file_path: Path) -> str:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing extra whitespace."""
        return re.sub(r'\s+', ' ', text).strip()

    def process_document(self, file_path: str) -> List[str]:
        """
        Process document and return chunks of text.
        
        Args:
            file_path (str): Path to the document
            
        Returns:
            List[str]: List of text chunks
            
        Raises:
            ValueError: If file format is not supported
            Exception: For any processing errors
        """
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            # Extract text based on file type
            if file_path.suffix.lower() == '.pdf':
                text = self._extract_pdf(file_path)
            elif file_path.suffix.lower() in ['.doc', '.docx']:
                text = self._extract_doc(file_path)
            else:  # .txt
                text = self._extract_txt(file_path)
            
            # Clean and chunk the text
            text = self._clean_text(text)
            return self._chunk_text(text)
            
        except Exception as e:
            raise Exception(f"Error processing {file_path}: {str(e)}")

    def get_document_info(self, file_path: str) -> dict:
        """
        Get basic information about the processed document.
        
        Args:
            file_path (str): Path to the document
            
        Returns:
            dict: Document information including chunk count and total characters
        """
        chunks = self.process_document(file_path)
        return {
            'chunk_count': len(chunks),
            'total_chars': sum(len(chunk) for chunk in chunks),
            'avg_chunk_size': sum(len(chunk) for chunk in chunks) / len(chunks) if chunks else 0
        }
    
#     # Initialize processor
# processor = DocumentProcessor(chunk_size=1000, overlap=100)

# try:
#     # Process a document
#     chunks = processor.process_document('/Users/khauneesh/synthetic-datagen/document_upload/transformers.pdf')
    
#     # Get document info
#     doc_info = processor.get_document_info('/Users/khauneesh/synthetic-datagen/document_upload/transformers.pdf')
#     print(f"Created {doc_info['chunk_count']} chunks")
#     print(f"Average chunk size: {doc_info['avg_chunk_size']:.2f} characters")
    
#     # Use chunks with your LLM
#     for i, chunk in enumerate(chunks):
#         print(f"Chunk {i + 1} length: {len(chunk)}")

# except Exception as e:
#     print(f"Error: {e}")