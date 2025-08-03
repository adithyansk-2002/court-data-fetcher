import re
from datetime import datetime, date
from typing import Tuple, Optional

def validate_case_number(case_number: str) -> Tuple[bool, Optional[str]]:
    """
    Validate case number format
    Returns: (is_valid, error_message)
    """
    if not case_number:
        return False, "Case number is required"
    
    if len(case_number) < 3:
        return False, "Case number must be at least 3 characters long"
    
    if len(case_number) > 50:
        return False, "Case number must be less than 50 characters"
    
    # Allow alphanumeric characters, spaces, hyphens, and dots
    if not re.match(r'^[A-Za-z0-9\s\-\.\/]+$', case_number):
        return False, "Case number contains invalid characters"
    
    return True, None

def validate_filing_year(year: int) -> Tuple[bool, Optional[str]]:
    """
    Validate filing year
    Returns: (is_valid, error_message)
    """
    current_year = datetime.now().year
    
    if not isinstance(year, int):
        return False, "Filing year must be a number"
    
    if year < 1950:
        return False, "Filing year cannot be before 1950"
    
    if year > current_year + 1:  # Allow next year for cases filed early
        return False, f"Filing year cannot be after {current_year + 1}"
    
    return True, None

def validate_case_type(case_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate case type
    Returns: (is_valid, error_message)
    """
    valid_case_types = [
        'WP(C)',  # Writ Petition (Civil)
        'WP(CRL)',  # Writ Petition (Criminal)
        'CRL',  # Criminal
        'CIVIL',  # Civil
        'LPA',  # Letters Patent Appeal
        'FAO',  # First Appeal from Order
        'RFA',  # Regular First Appeal
        'CM',  # Civil Miscellaneous
        'CRL.M.C.',  # Criminal Miscellaneous Case
        'CRL.A.',  # Criminal Appeal
        'CIVIL.A.',  # Civil Appeal
        'COMP.A.',  # Company Appeal
        'ARB.A.',  # Arbitration Appeal
        'TAX.A.',  # Tax Appeal
        'EXCISE.A.',  # Excise Appeal
        'CUSTOMS.A.',  # Customs Appeal
        'SERVICE.A.',  # Service Tax Appeal
        'COMP.P.',  # Company Petition
        'ARB.P.',  # Arbitration Petition
        'REV.P.',  # Revision Petition
        'S.L.P.',  # Special Leave Petition
        'MISC.',  # Miscellaneous
        'ORIGINAL',  # Original Petition
        'REVIEW',  # Review Petition
    ]
    
    if not case_type:
        return False, "Case type is required"
    
    if case_type not in valid_case_types:
        return False, f"Invalid case type. Must be one of: {', '.join(valid_case_types)}"
    
    return True, None

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '{', '}', '[', ']']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def validate_form_data(case_type: str, case_number: str, filing_year: int) -> Tuple[bool, Optional[str]]:
    """
    Validate all form data at once
    Returns: (is_valid, error_message)
    """
    # Validate case type
    is_valid, error = validate_case_type(case_type)
    if not is_valid:
        return False, error
    
    # Validate case number
    is_valid, error = validate_case_number(case_number)
    if not is_valid:
        return False, error
    
    # Validate filing year
    is_valid, error = validate_filing_year(filing_year)
    if not is_valid:
        return False, error
    
    return True, None

def format_case_number(case_number: str) -> str:
    """
    Format case number for display
    """
    if not case_number:
        return ""
    
    # Remove extra spaces and normalize
    case_number = ' '.join(case_number.split())
    
    # Convert to title case for better readability
    return case_number.title()

def get_case_types() -> list:
    """
    Get list of valid case types
    """
    return [
        'WP(C)',  # Writ Petition (Civil)
        'WP(CRL)',  # Writ Petition (Criminal)
        'CRL',  # Criminal
        'CIVIL',  # Civil
        'LPA',  # Letters Patent Appeal
        'FAO',  # First Appeal from Order
        'RFA',  # Regular First Appeal
        'CM',  # Civil Miscellaneous
        'CRL.M.C.',  # Criminal Miscellaneous Case
        'CRL.A.',  # Criminal Appeal
        'CIVIL.A.',  # Civil Appeal
        'COMP.A.',  # Company Appeal
        'ARB.A.',  # Arbitration Appeal
        'TAX.A.',  # Tax Appeal
        'EXCISE.A.',  # Excise Appeal
        'CUSTOMS.A.',  # Customs Appeal
        'SERVICE.A.',  # Service Tax Appeal
        'COMP.P.',  # Company Petition
        'ARB.P.',  # Arbitration Petition
        'REV.P.',  # Revision Petition
        'S.L.P.',  # Special Leave Petition
        'MISC.',  # Miscellaneous
        'ORIGINAL',  # Original Petition
        'REVIEW',  # Review Petition
    ]

def get_year_range() -> list:
    """
    Get range of years for filing year dropdown
    """
    current_year = datetime.now().year
    return list(range(current_year, 1949, -1))  # From current year to 1950 