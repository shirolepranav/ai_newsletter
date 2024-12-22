import PyPDF2
from docx import Document
import pandas as pd
import io

class DocumentProcessor:
    """Handles processing of uploaded documents (PDF, Word, Excel)"""
    
    @staticmethod
    def process_pdf(file_content):
        """Extract text from PDF file"""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    @staticmethod
    def process_docx(file_content):
        """Extract text from Word document"""
        doc = Document(io.BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    @staticmethod
    def process_excel(file_content):
        """Extract text from Excel file"""
        df = pd.read_excel(io.BytesIO(file_content))
        # Convert DataFrame to string representation
        return df.to_string()

    def process_document(self, file):
        """Process uploaded document based on file type"""
        content = file.read()
        file_type = file.name.split('.')[-1].lower()
        
        try:
            if file_type == 'pdf':
                return self.process_pdf(content)
            elif file_type in ['doc', 'docx']:
                return self.process_docx(content)
            elif file_type in ['xls', 'xlsx']:
                return self.process_excel(content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise Exception(f"Error processing {file_type} file: {str(e)}")