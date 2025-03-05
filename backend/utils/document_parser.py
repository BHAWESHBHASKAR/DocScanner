import os
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import io

class DocumentParser:
    @staticmethod
    def parse_file(file):
        """
        Parse different types of files and extract text content
        Supported formats: .txt, .pdf, .doc, .docx
        """
        filename = file.filename.lower()
        content = ""
        
        try:
            # Read the entire file content first
            file_content = file.read()
            if not file_content:
                raise ValueError("Empty file uploaded")
            
            # Create a memory buffer that we can seek
            file_buffer = io.BytesIO(file_content)
            
            if filename.endswith('.txt'):
                try:
                    content = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    raise ValueError("Invalid text file encoding. Please ensure it's UTF-8 encoded.")
                    
            elif filename.endswith('.pdf'):
                try:
                    # Create PDF reader object
                    pdf_reader = PdfReader(file_buffer)
                    if len(pdf_reader.pages) == 0:
                        raise ValueError("PDF file contains no pages")
                        
                    # Extract text from all pages
                    content = ""
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            content += page_text + "\n"
                            
                    if not content.strip():
                        raise ValueError("Could not extract any text from PDF file")
                        
                except Exception as e:
                    raise ValueError(f"Error reading PDF file: {str(e)}")
                    
            elif filename.endswith(('.doc', '.docx')):
                try:
                    # Create DOCX document object
                    doc = DocxDocument(file_buffer)
                    
                    # Extract text from all paragraphs
                    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                    if not paragraphs:
                        raise ValueError("Document contains no text")
                        
                    content = "\n".join(paragraphs)
                    
                except Exception as e:
                    raise ValueError(f"Error reading document file: {str(e)}")
            
            else:
                raise ValueError("Unsupported file format")
            
            return content.strip()
        
        except Exception as e:
            raise Exception(f"Error parsing file: {str(e)}")

    @staticmethod
    def get_allowed_extensions():
        """Return list of allowed file extensions"""
        return {'txt', 'pdf', 'doc', 'docx'}
