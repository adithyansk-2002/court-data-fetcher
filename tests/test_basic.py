import pytest
import os
import sys
from flask import Flask

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.database import db, Query, Download
from utils.validators import validate_case_number, validate_filing_year, validate_case_type
from utils.pdf_handler import PDFHandler

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

class TestBasicFunctionality:
    """Test basic application functionality."""
    
    def test_home_page(self, client):
        """Test that the home page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Court Data Fetcher' in response.data
    
    def test_search_history_page(self, client):
        """Test that the search history page loads successfully."""
        response = client.get('/search-history')
        assert response.status_code == 200
        assert b'Search History' in response.data
    
    def test_api_case_types(self, client):
        """Test the case types API endpoint."""
        response = client.get('/api/case-types')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'case_types' in data
        assert len(data['case_types']) > 0
    
    def test_api_search_history(self, client):
        """Test the search history API endpoint."""
        response = client.get('/api/search-history')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'history' in data

class TestValidation:
    """Test input validation functions."""
    
    def test_validate_case_number_valid(self):
        """Test valid case number validation."""
        valid_cases = [
            "123/2023",
            "ABC-456",
            "Criminal Case 789",
            "WP(C) 123/2023"
        ]
        
        for case in valid_cases:
            is_valid, error = validate_case_number(case)
            assert is_valid, f"Case number '{case}' should be valid: {error}"
    
    def test_validate_case_number_invalid(self):
        """Test invalid case number validation."""
        invalid_cases = [
            "",  # Empty
            "12",  # Too short
            "A" * 51,  # Too long
            "Case#123",  # Invalid characters
            "Case<script>alert('xss')</script>"  # XSS attempt
        ]
        
        for case in invalid_cases:
            is_valid, error = validate_case_number(case)
            assert not is_valid, f"Case number '{case}' should be invalid"
            assert error is not None
    
    def test_validate_filing_year_valid(self):
        """Test valid filing year validation."""
        from datetime import datetime
        current_year = datetime.now().year
        
        valid_years = [1950, 2000, current_year, current_year + 1]
        
        for year in valid_years:
            is_valid, error = validate_filing_year(year)
            assert is_valid, f"Year {year} should be valid: {error}"
    
    def test_validate_filing_year_invalid(self):
        """Test invalid filing year validation."""
        from datetime import datetime
        current_year = datetime.now().year
        
        invalid_years = [1949, current_year + 2, "not a number", None]
        
        for year in invalid_years:
            is_valid, error = validate_filing_year(year)
            assert not is_valid, f"Year {year} should be invalid"
            assert error is not None
    
    def test_validate_case_type_valid(self):
        """Test valid case type validation."""
        valid_types = ["Civil", "Criminal", "Writ Petition"]
        
        for case_type in valid_types:
            is_valid, error = validate_case_type(case_type)
            assert is_valid, f"Case type '{case_type}' should be valid: {error}"
    
    def test_validate_case_type_invalid(self):
        """Test invalid case type validation."""
        invalid_types = ["", "Invalid Type", "Civil Case", None]
        
        for case_type in invalid_types:
            is_valid, error = validate_case_type(case_type)
            assert not is_valid, f"Case type '{case_type}' should be invalid"
            assert error is not None

class TestDatabase:
    """Test database functionality."""
    
    def test_query_creation(self, app):
        """Test creating a query record."""
        with app.app_context():
            query = Query(
                case_type="Civil",
                case_number="123/2023",
                filing_year=2023,
                status="success"
            )
            db.session.add(query)
            db.session.commit()
            
            assert query.id is not None
            assert query.case_type == "Civil"
            assert query.case_number == "123/2023"
            assert query.filing_year == 2023
            assert query.status == "success"
    
    def test_query_to_dict(self, app):
        """Test query to_dict method."""
        with app.app_context():
            query = Query(
                case_type="Criminal",
                case_number="456/2022",
                filing_year=2022,
                status="error",
                error_message="Case not found"
            )
            db.session.add(query)
            db.session.commit()
            
            query_dict = query.to_dict()
            assert query_dict['case_type'] == "Criminal"
            assert query_dict['case_number'] == "456/2022"
            assert query_dict['filing_year'] == 2022
            assert query_dict['status'] == "error"
            assert query_dict['error_message'] == "Case not found"
    
    def test_download_creation(self, app):
        """Test creating a download record."""
        with app.app_context():
            # First create a query
            query = Query(
                case_type="Civil",
                case_number="123/2023",
                filing_year=2023
            )
            db.session.add(query)
            db.session.commit()
            
            # Then create a download
            download = Download(
                query_id=query.id,
                pdf_url="https://example.com/document.pdf",
                local_path="/path/to/local/file.pdf",
                filename="document.pdf",
                file_size=1024,
                status="success"
            )
            db.session.add(download)
            db.session.commit()
            
            assert download.id is not None
            assert download.query_id == query.id
            assert download.pdf_url == "https://example.com/document.pdf"
            assert download.file_size == 1024

class TestPDFHandler:
    """Test PDF handler functionality."""
    
    def test_pdf_handler_initialization(self):
        """Test PDF handler initialization."""
        handler = PDFHandler("test_downloads")
        assert handler.download_folder == "test_downloads"
    
    def test_format_file_size(self):
        """Test file size formatting."""
        handler = PDFHandler()
        
        assert handler.format_file_size(0) == "0 B"
        assert handler.format_file_size(1024) == "1.0 KB"
        assert handler.format_file_size(1024 * 1024) == "1.0 MB"
        assert handler.format_file_size(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_is_valid_pdf(self, tmp_path):
        """Test PDF validation."""
        handler = PDFHandler()
        
        # Create a fake PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b'%PDF-1.4\nfake pdf content')
        
        assert handler.is_valid_pdf(str(pdf_file))
        
        # Test with non-PDF file
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("This is not a PDF")
        
        assert not handler.is_valid_pdf(str(txt_file))

if __name__ == '__main__':
    pytest.main([__file__]) 