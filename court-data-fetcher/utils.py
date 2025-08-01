import re
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def validate_case_number(case_number: str) -> bool:
    """
    Validate case number format
    
    Args:
        case_number (str): Case number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not case_number or not isinstance(case_number, str):
        return False
    
    # Common case number patterns
    patterns = [
        # W.P.(C) 1234/2023
        r'^[A-Z\.]+\([A-Z]+\)\s+\d+/\d{4}$',
        # LPA 123/2023
        r'^[A-Z\.]+\s+\d+/\d{4}$',
        # C.M.(M) 123 of 2023
        r'^[A-Z\.]+\([A-Z]+\)\s+\d+\s+of\s+\d{4}$',
        # CRL.A. 123-2023
        r'^[A-Z\.]+\s+\d+-\d{4}$',
        # Generic pattern
        r'^[A-Z\.]+\s+\d+[/\-]\d{4}$'
    ]
    
    for pattern in patterns:
        if re.match(pattern, case_number, re.IGNORECASE):
            return True
    
    return False

def format_date(date_input: Any) -> Optional[str]:
    """
    Format date input to readable string
    
    Args:
        date_input: Date input (string, datetime, or date object)
        
    Returns:
        str: Formatted date string or None
    """
    if not date_input:
        return None
    
    try:
        # If it's already a string, try to parse it
        if isinstance(date_input, str):
            # Try different date formats
            date_formats = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%Y/%m/%d',
                '%d/%m/%y',
                '%d-%m-%y'
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_input.strip(), fmt)
                    return parsed_date.strftime('%d %B %Y')
                except ValueError:
                    continue
            
            return date_input  # Return as is if can't parse
        
        # If it's a datetime or date object
        elif hasattr(date_input, 'strftime'):
            return date_input.strftime('%d %B %Y')
        
        return str(date_input)
        
    except Exception as e:
        logger.error(f"Error formatting date {date_input}: {str(e)}")
        return str(date_input) if date_input else None

def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse date string to datetime object
    
    Args:
        date_string (str): Date string to parse
        
    Returns:
        datetime: Parsed datetime object or None
    """
    if not date_string:
        return None
    
    try:
        # Try different date formats
        date_formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y/%m/%d',
            '%d/%m/%y',
            '%d-%m-%y',
            '%d %B %Y',
            '%B %d, %Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue
        
        return None
        
    except Exception as e:
        logger.error(f"Error parsing date {date_string}: {str(e)}")
        return None

def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-\.\(\)\/]', '', text)
    
    return text

def extract_case_type(case_number: str) -> str:
    """
    Extract case type from case number
    
    Args:
        case_number (str): Case number
        
    Returns:
        str: Extracted case type
    """
    if not case_number:
        return "Unknown"
    
    # Common case types
    case_types = [
        'W.P.(C)', 'W.P.(CRL)', 'W.P.(MD)', 'W.P.(CIVIL)', 'W.P.(CRIMINAL)',
        'C.M.(M)', 'C.M.(W)', 'C.M.(MAIN)', 'C.M.(APPL)', 'C.M.(NO.)',
        'LPA', 'FAO', 'RFA', 'CRL.A.', 'CRL.M.C.', 'CRL.REV.P.',
        'C.R.P.', 'C.M.', 'O.A.', 'T.A.', 'A.A.', 'E.P.'
    ]
    
    # Try to match exact case types
    for case_type in case_types:
        if case_number.upper().startswith(case_type.upper()):
            return case_type
    
    # Extract first part as case type
    parts = case_number.split()
    if parts:
        return parts[0]
    
    return "Unknown"

def normalize_case_number(case_number: str) -> str:
    """
    Normalize case number format
    
    Args:
        case_number (str): Case number to normalize
        
    Returns:
        str: Normalized case number
    """
    if not case_number:
        return ""
    
    # Remove extra spaces and normalize
    case_number = re.sub(r'\s+', ' ', case_number.strip())
    
    # Convert to uppercase for consistency
    case_number = case_number.upper()
    
    return case_number

def validate_party_name(party_name: str) -> bool:
    """
    Validate party name
    
    Args:
        party_name (str): Party name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not party_name or not isinstance(party_name, str):
        return False
    
    # Party name should be at least 2 characters and contain letters
    if len(party_name.strip()) < 2:
        return False
    
    # Should contain at least one letter
    if not re.search(r'[a-zA-Z]', party_name):
        return False
    
    return True

def sanitize_input(input_string: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        input_string (str): Input string to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', input_string)
    
    # Remove extra whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized.strip())
    
    return sanitized

def format_case_status(status: str) -> str:
    """
    Format case status for display
    
    Args:
        status (str): Raw status string
        
    Returns:
        str: Formatted status
    """
    if not status:
        return "Unknown"
    
    # Common status mappings
    status_mappings = {
        'pending': 'Pending',
        'disposed': 'Disposed',
        'dismissed': 'Dismissed',
        'closed': 'Closed',
        'active': 'Active',
        'inactive': 'Inactive',
        'withdrawn': 'Withdrawn',
        'settled': 'Settled'
    }
    
    status_lower = status.lower()
    for key, value in status_mappings.items():
        if key in status_lower:
            return value
    
    # Return title case if no mapping found
    return status.title()

def get_case_status_color(status: str) -> str:
    """
    Get CSS color class for case status
    
    Args:
        status (str): Case status
        
    Returns:
        str: CSS color class
    """
    if not status:
        return "status-unknown"
    
    status_lower = status.lower()
    
    if any(word in status_lower for word in ['pending', 'active', 'ongoing']):
        return "status-pending"
    elif any(word in status_lower for word in ['disposed', 'closed', 'settled']):
        return "status-disposed"
    elif any(word in status_lower for word in ['dismissed', 'withdrawn']):
        return "status-dismissed"
    else:
        return "status-unknown"

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def generate_search_suggestions(query: str) -> list:
    """
    Generate search suggestions based on query
    
    Args:
        query (str): Search query
        
    Returns:
        list: List of suggestions
    """
    suggestions = []
    
    if not query or len(query) < 2:
        return suggestions
    
    # Common case types
    case_types = [
        'W.P.(C)', 'W.P.(CRL)', 'LPA', 'FAO', 'RFA', 
        'CRL.A.', 'C.M.(M)', 'C.M.(W)'
    ]
    
    # Add case type suggestions
    for case_type in case_types:
        if case_type.lower().startswith(query.lower()):
            suggestions.append(f"{case_type} ")
    
    # Add year suggestions
    current_year = datetime.now().year
    for year in range(current_year, current_year - 5, -1):
        if str(year).startswith(query):
            suggestions.append(str(year))
    
    return suggestions[:5]  # Limit to 5 suggestions
