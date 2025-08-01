import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DelhiHighCourtScraper:
    """
    Scraper for Delhi High Court case information
    """
    
    def __init__(self):
        self.base_url = "https://delhihighcourt.nic.in"
        self.search_url = f"{self.base_url}/case.asp"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def search_cases(self, case_number: str = "", party_name: str = "") -> List[Dict]:
        """
        Search for cases by case number or party name
        
        Args:
            case_number (str): Case number to search for
            party_name (str): Party name to search for
            
        Returns:
            List[Dict]: List of case dictionaries
        """
        try:
            # For demonstration purposes, return mock data
            # In a real implementation, this would scrape the actual website
            mock_cases = self._get_mock_cases(case_number, party_name)
            
            if mock_cases:
                logger.info(f"Found {len(mock_cases)} mock cases for search: case_number='{case_number}', party_name='{party_name}'")
                return mock_cases
            else:
                logger.info(f"No mock cases found for search: case_number='{case_number}', party_name='{party_name}'")
                return []
                
        except Exception as e:
            logger.error(f"Error searching cases: {str(e)}")
            return []
    
    def _get_mock_cases(self, case_number: str = "", party_name: str = "") -> List[Dict]:
        """
        Get mock case data for demonstration
        
        Args:
            case_number (str): Case number to search for
            party_name (str): Party name to search for
            
        Returns:
            List[Dict]: List of mock case dictionaries
        """
        mock_cases = [
            {
                'case_number': 'W.P.(C) 1040/2023',
                'petitioner': 'Reliance Industries Limited',
                'respondent': 'Union of India & Ors.',
                'filing_date': '2023-03-15',
                'status': 'Pending',
                'court': 'Delhi High Court',
                'case_type': 'W.P.(C)',
                'judge': 'Hon\'ble Mr. Justice Rajiv Shakdher',
                'next_hearing': '2024-01-15'
            },
            {
                'case_number': 'LPA 163/2023',
                'petitioner': 'State of Delhi',
                'respondent': 'Delhi Development Authority',
                'filing_date': '2023-02-20',
                'status': 'Disposed',
                'court': 'Delhi High Court',
                'case_type': 'LPA',
                'judge': 'Hon\'ble Mr. Justice Vipin Sanghi',
                'next_hearing': None
            },
            {
                'case_number': 'FAO 456/2022',
                'petitioner': 'John Doe',
                'respondent': 'ABC Corporation',
                'filing_date': '2022-11-10',
                'status': 'Pending',
                'court': 'Delhi High Court',
                'case_type': 'FAO',
                'judge': 'Hon\'ble Ms. Justice Rekha Palli',
                'next_hearing': '2024-01-20'
            },
            {
                'case_number': 'CRL.A. 789-2021',
                'petitioner': 'Central Bureau of Investigation',
                'respondent': 'XYZ Limited',
                'filing_date': '2021-08-05',
                'status': 'Pending',
                'court': 'Delhi High Court',
                'case_type': 'CRL.A.',
                'judge': 'Hon\'ble Mr. Justice Siddharth Mridul',
                'next_hearing': '2024-01-25'
            },
            {
                'case_number': 'C.M.(M) 123/2023',
                'petitioner': 'Delhi Metro Rail Corporation',
                'respondent': 'Municipal Corporation of Delhi',
                'filing_date': '2023-04-12',
                'status': 'Pending',
                'court': 'Delhi High Court',
                'case_type': 'C.M.(M)',
                'judge': 'Hon\'ble Mr. Justice Yashwant Varma',
                'next_hearing': '2024-01-30'
            }
        ]
        
        # Filter based on search criteria
        filtered_cases = []
        
        for case in mock_cases:
            # Check if case number matches
            if case_number and case_number.lower() in case['case_number'].lower():
                filtered_cases.append(case)
                continue
            
            # Check if party name matches
            if party_name:
                party_lower = party_name.lower()
                petitioner_lower = case['petitioner'].lower()
                respondent_lower = case['respondent'].lower()
                
                if (party_lower in petitioner_lower or 
                    party_lower in respondent_lower or
                    petitioner_lower in party_lower or
                    respondent_lower in party_lower):
                    filtered_cases.append(case)
                    continue
            
            # If no specific search criteria, return all cases
            if not case_number and not party_name:
                filtered_cases.append(case)
        
        return filtered_cases[:5]  # Limit to 5 results
    
    def _search_by_case_number(self, case_number: str) -> List[Dict]:
        """
        Search cases by case number
        
        Args:
            case_number (str): Case number to search
            
        Returns:
            List[Dict]: List of matching cases
        """
        try:
            # Parse case number components
            case_info = self._parse_case_number(case_number)
            if not case_info:
                return []
            
            # First, get the search page to extract any required tokens
            response = self.session.get(self.search_url, timeout=30)
            response.raise_for_status()
            
            # Parse the page to extract form fields
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Prepare search data based on actual form structure
            search_data = {
                'case_type': case_info['case_type'],
                'case_number': case_info['number'],
                'filing_year': case_info['year'],
                'submit': 'Search'
            }
            
            # Look for hidden fields like viewstate, etc.
            hidden_inputs = soup.find_all('input', type='hidden')
            for hidden in hidden_inputs:
                name = hidden.get('name')
                value = hidden.get('value', '')
                if name:
                    search_data[name] = value
            
            # Make search request
            response = self.session.post(self.search_url, data=search_data, timeout=30)
            response.raise_for_status()
            
            # Parse response
            cases = self._parse_search_results(response.text)
            return cases
            
        except Exception as e:
            logger.error(f"Error searching by case number {case_number}: {str(e)}")
            return []
    
    def _search_by_party_name(self, party_name: str) -> List[Dict]:
        """
        Search cases by party name
        
        Args:
            party_name (str): Party name to search
            
        Returns:
            List[Dict]: List of matching cases
        """
        try:
            # First, get the search page to extract any required tokens
            response = self.session.get(self.search_url, timeout=30)
            response.raise_for_status()
            
            # Parse the page to extract form fields
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Prepare search data based on actual form structure
            search_data = {
                'party_name': party_name,
                'search_type': 'party',
                'submit': 'Search'
            }
            
            # Look for hidden fields like viewstate, etc.
            hidden_inputs = soup.find_all('input', type='hidden')
            for hidden in hidden_inputs:
                name = hidden.get('name')
                value = hidden.get('value', '')
                if name:
                    search_data[name] = value
            
            # Make search request
            response = self.session.post(self.search_url, data=search_data, timeout=30)
            response.raise_for_status()
            
            # Parse response
            cases = self._parse_search_results(response.text)
            return cases
            
        except Exception as e:
            logger.error(f"Error searching by party name {party_name}: {str(e)}")
            return []
    
    def _parse_case_number(self, case_number: str) -> Optional[Dict]:
        """
        Parse case number into components
        
        Args:
            case_number (str): Case number string
            
        Returns:
            Dict: Parsed case number components or None
        """
        # Common case type patterns
        case_types = [
            'W.P.(C)', 'W.P.(CRL)', 'W.P.(MD)', 'W.P.(CIVIL)', 'W.P.(CRIMINAL)',
            'C.M.(M)', 'C.M.(W)', 'C.M.(MAIN)', 'C.M.(APPL)', 'C.M.(NO.)',
            'LPA', 'FAO', 'RFA', 'CRL.A.', 'CRL.M.C.', 'CRL.REV.P.',
            'C.R.P.', 'C.M.', 'O.A.', 'T.A.', 'A.A.', 'E.P.'
        ]
        
        # Try to match case number pattern
        for case_type in case_types:
            pattern = rf"^{re.escape(case_type)}\s*(\d+)/(\d{{4}})$"
            match = re.match(pattern, case_number, re.IGNORECASE)
            
            if match:
                return {
                    'case_type': case_type,
                    'number': match.group(1),
                    'year': match.group(2)
                }
        
        # Try alternative patterns
        patterns = [
            r"^([A-Z\.]+)\s*(\d+)/(\d{4})$",
            r"^([A-Z\.]+)\s*(\d+)\s*of\s*(\d{4})$",
            r"^([A-Z\.]+)\s*(\d+)-(\d{4})$"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, case_number, re.IGNORECASE)
            if match:
                return {
                    'case_type': match.group(1).strip(),
                    'number': match.group(2),
                    'year': match.group(3)
                }
        
        return None
    
    def _parse_search_results(self, html_content: str) -> List[Dict]:
        """
        Parse HTML search results into case dictionaries
        
        Args:
            html_content (str): HTML content from search response
            
        Returns:
            List[Dict]: List of parsed case dictionaries
        """
        cases = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check if there's a CAPTCHA
            if 'captcha' in html_content.lower() or 'verify' in html_content.lower():
                logger.warning("CAPTCHA detected on the page")
                return []
            
            # Look for case result tables - Delhi High Court typically uses tables
            tables = soup.find_all('table')
            
            for table in tables:
                # Look for rows that contain case information
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:  # At least 3 columns for case info
                        case_data = self._extract_case_from_row(cells)
                        if case_data:
                            cases.append(case_data)
            
            # If no structured results found in tables, try to extract from text
            if not cases:
                cases = self._extract_from_text(html_content)
            
            # If still no cases, try alternative parsing methods
            if not cases:
                cases = self._extract_from_divs(soup)
            
            return cases
            
        except Exception as e:
            logger.error(f"Error parsing search results: {str(e)}")
            return []
    
    def _extract_case_from_row(self, cells) -> Optional[Dict]:
        """
        Extract case data from table row cells
        
        Args:
            cells: List of table cells
            
        Returns:
            Dict: Case data dictionary or None
        """
        try:
            # Look for patterns in the cells
            case_number = None
            petitioner = None
            respondent = None
            filing_date = None
            status = None
            
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # Look for case number pattern
                if not case_number and re.search(r'[A-Z\.]+\([A-Z]+\)\s+\d+/\d{4}', cell_text):
                    case_number = cell_text
                
                # Look for petitioner/respondent patterns
                elif 'petitioner' in cell_text.lower() or 'vs' in cell_text.lower():
                    if i + 1 < len(cells):
                        petitioner = cells[i + 1].get_text(strip=True)
                
                # Look for dates
                elif re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', cell_text):
                    if not filing_date:
                        filing_date = cell_text
                
                # Look for status
                elif any(status_word in cell_text.lower() for status_word in ['pending', 'disposed', 'dismissed', 'closed']):
                    status = cell_text
            
            if case_number:
                return {
                    'case_number': case_number,
                    'petitioner': petitioner or 'N/A',
                    'respondent': respondent or 'N/A',
                    'filing_date': self._parse_date(filing_date) if filing_date else None,
                    'status': status or 'Unknown',
                    'court': 'Delhi High Court',
                    'case_type': self._extract_case_type(case_number),
                    'judge': None,
                    'next_hearing': None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting case from row: {str(e)}")
            return None
    
    def _extract_from_divs(self, soup) -> List[Dict]:
        """
        Extract case information from div elements
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List[Dict]: List of extracted cases
        """
        cases = []
        
        try:
            # Look for divs that might contain case information
            case_divs = soup.find_all('div', class_=re.compile(r'case|result|row|item'))
            
            for div in case_divs:
                case_data = self._extract_case_data(div)
                if case_data:
                    cases.append(case_data)
            
            return cases
            
        except Exception as e:
            logger.error(f"Error extracting from divs: {str(e)}")
            return []
    
    def _extract_case_data(self, element) -> Optional[Dict]:
        """
        Extract case data from HTML element
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Dict: Case data dictionary or None
        """
        try:
            # Try to find case information in the element
            case_number = self._extract_text(element, ['case-number', 'case_no', 'case_number'])
            petitioner = self._extract_text(element, ['petitioner', 'petitioner_name'])
            respondent = self._extract_text(element, ['respondent', 'respondent_name'])
            filing_date = self._extract_text(element, ['filing_date', 'date_filed'])
            status = self._extract_text(element, ['status', 'case_status'])
            
            if case_number:
                return {
                    'case_number': case_number,
                    'petitioner': petitioner or 'N/A',
                    'respondent': respondent or 'N/A',
                    'filing_date': self._parse_date(filing_date) if filing_date else None,
                    'status': status or 'Unknown',
                    'court': 'Delhi High Court',
                    'case_type': self._extract_case_type(case_number),
                    'judge': self._extract_text(element, ['judge', 'judge_name']),
                    'next_hearing': self._extract_text(element, ['next_hearing', 'hearing_date'])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting case data: {str(e)}")
            return None
    
    def _extract_text(self, element, class_names: List[str]) -> Optional[str]:
        """
        Extract text from element using multiple possible class names
        
        Args:
            element: BeautifulSoup element
            class_names: List of possible class names
            
        Returns:
            str: Extracted text or None
        """
        for class_name in class_names:
            found = element.find(class_=class_name)
            if found:
                return found.get_text(strip=True)
        
        return None
    
    def _extract_case_type(self, case_number: str) -> str:
        """
        Extract case type from case number
        
        Args:
            case_number (str): Case number
            
        Returns:
            str: Case type
        """
        if not case_number:
            return 'Unknown'
        
        # Extract case type from beginning of case number
        parts = case_number.split()
        if parts:
            return parts[0]
        
        return 'Unknown'
    
    def _parse_date(self, date_string: str) -> Optional[str]:
        """
        Parse date string into standard format
        
        Args:
            date_string (str): Date string to parse
            
        Returns:
            str: Parsed date in YYYY-MM-DD format or None
        """
        if not date_string:
            return None
        
        try:
            # Try different date formats
            date_formats = [
                '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d',
                '%d/%m/%y', '%d-%m-%y', '%Y/%m/%d'
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_string.strip(), fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing date {date_string}: {str(e)}")
            return None
    
    def _extract_from_text(self, html_content: str) -> List[Dict]:
        """
        Extract case information from plain text when structured parsing fails
        
        Args:
            html_content (str): HTML content
            
        Returns:
            List[Dict]: List of extracted cases
        """
        cases = []
        
        try:
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Look for case number patterns
            case_patterns = [
                r'([A-Z\.]+\s+\d+/\d{4})',
                r'([A-Z\.]+\s+\d+\s+of\s+\d{4})',
                r'([A-Z\.]+\s+\d+-\d{4})'
            ]
            
            for pattern in case_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    case_data = {
                        'case_number': match.strip(),
                        'petitioner': 'N/A',
                        'respondent': 'N/A',
                        'filing_date': None,
                        'status': 'Unknown',
                        'court': 'Delhi High Court',
                        'case_type': self._extract_case_type(match),
                        'judge': None,
                        'next_hearing': None
                    }
                    cases.append(case_data)
            
            return cases
            
        except Exception as e:
            logger.error(f"Error extracting from text: {str(e)}")
            return []
    
    def get_case_details(self, case_number: str) -> Optional[Dict]:
        """
        Get detailed information for a specific case
        
        Args:
            case_number (str): Case number
            
        Returns:
            Dict: Detailed case information or None
        """
        try:
            cases = self.search_cases(case_number=case_number)
            if cases:
                return cases[0]  # Return first match
            return None
            
        except Exception as e:
            logger.error(f"Error getting case details for {case_number}: {str(e)}")
            return None
    
    def test_connection(self) -> Dict:
        """
        Test connection to Delhi High Court website
        
        Returns:
            Dict: Connection test results
        """
        try:
            # Test basic connection
            response = self.session.get(self.search_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for CAPTCHA
            has_captcha = 'captcha' in response.text.lower() or 'verify' in response.text.lower()
            
            # Look for form elements
            forms = soup.find_all('form')
            form_count = len(forms)
            
            # Look for input fields
            inputs = soup.find_all('input')
            input_count = len(inputs)
            
            # Check page title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else 'No title found'
            
            return {
                'status': 'success',
                'status_code': response.status_code,
                'has_captcha': has_captcha,
                'form_count': form_count,
                'input_count': input_count,
                'title': title_text,
                'url': self.search_url,
                'content_length': len(response.text)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'url': self.search_url
            }
    
    def __del__(self):
        """Cleanup session on object destruction"""
        if hasattr(self, 'session'):
            self.session.close() 