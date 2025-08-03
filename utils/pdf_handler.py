import os
import requests
import PyPDF2
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib
from urllib.parse import urlparse, urljoin
import logging

class PDFHandler:
    """Handler for downloading and processing PDF files"""
    
    def __init__(self, download_folder: str = "static/downloads"):
        self.download_folder = download_folder
        self.ensure_download_folder()
        
    def ensure_download_folder(self):
        """Ensure download folder exists"""
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder, exist_ok=True)
    
    def download_pdf(self, url: str, session: requests.Session = None) -> Dict[str, Any]:
        """
        Download PDF from URL
        Returns: Dict with status, local_path, filename, file_size, error_message
        """
        try:
            # Use provided session or create new one
            if session is None:
                session = requests.Session()
            
            # Set headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/pdf,application/octet-stream,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Download the PDF
            response = session.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check if response is actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                return {
                    'status': 'error',
                    'error_message': 'URL does not point to a PDF file',
                    'local_path': None,
                    'filename': None,
                    'file_size': None
                }
            
            # Generate filename from URL and timestamp
            parsed_url = urlparse(url)
            original_filename = os.path.basename(parsed_url.path)
            if not original_filename or not original_filename.lower().endswith('.pdf'):
                original_filename = 'document.pdf'
            
            # Create unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"{timestamp}_{filename_hash}_{original_filename}"
            
            local_path = os.path.join(self.download_folder, filename)
            
            # Save the PDF
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(local_path)
            
            return {
                'status': 'success',
                'local_path': local_path,
                'filename': filename,
                'file_size': file_size,
                'error_message': None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'error_message': f'Download failed: {str(e)}',
                'local_path': None,
                'filename': None,
                'file_size': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'error_message': f'Unexpected error: {str(e)}',
                'local_path': None,
                'filename': None,
                'file_size': None
            }
    
    def extract_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF file
        Returns: Dict with metadata or error information
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get basic info
                info = pdf_reader.metadata
                num_pages = len(pdf_reader.pages)
                
                # Extract text from first page for preview
                first_page_text = ""
                if num_pages > 0:
                    try:
                        first_page = pdf_reader.pages[0]
                        first_page_text = first_page.extract_text()[:500]  # First 500 chars
                    except:
                        first_page_text = "Text extraction failed"
                
                return {
                    'status': 'success',
                    'num_pages': num_pages,
                    'title': info.get('/Title', 'Unknown'),
                    'author': info.get('/Author', 'Unknown'),
                    'subject': info.get('/Subject', ''),
                    'creator': info.get('/Creator', ''),
                    'producer': info.get('/Producer', ''),
                    'creation_date': info.get('/CreationDate', ''),
                    'modification_date': info.get('/ModDate', ''),
                    'first_page_preview': first_page_text,
                    'error_message': None
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error_message': f'Failed to extract PDF metadata: {str(e)}',
                'num_pages': 0,
                'title': 'Unknown',
                'author': 'Unknown',
                'subject': '',
                'creator': '',
                'producer': '',
                'creation_date': '',
                'modification_date': '',
                'first_page_preview': '',
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic file information
        """
        try:
            stat = os.stat(file_path)
            return {
                'file_size': stat.st_size,
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'exists': True
            }
        except FileNotFoundError:
            return {
                'file_size': 0,
                'created_time': None,
                'modified_time': None,
                'exists': False
            }
    
    def cleanup_old_files(self, max_age_days: int = 30):
        """
        Clean up old PDF files
        """
        try:
            current_time = datetime.now()
            for filename in os.listdir(self.download_folder):
                if filename.lower().endswith('.pdf'):
                    file_path = os.path.join(self.download_folder, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if (current_time - file_time).days > max_age_days:
                        os.remove(file_path)
                        logging.info(f"Cleaned up old file: {filename}")
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human readable format
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def is_valid_pdf(self, file_path: str) -> bool:
        """
        Check if file is a valid PDF
        """
        try:
            with open(file_path, 'rb') as file:
                # Check PDF magic number
                header = file.read(4)
                return header == b'%PDF'
        except:
            return False 