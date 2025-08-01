import requests
from bs4 import BeautifulSoup
import re

def test_delhi_high_court():
    """Test Delhi High Court website accessibility"""
    
    # Try different possible URLs
    urls_to_test = [
        "https://delhihighcourt.nic.in/case.asp",
        "https://delhihighcourt.nic.in/case_status.asp",
        "https://delhihighcourt.nic.in/case-status",
        "https://delhihighcourt.nic.in/case_status",
        "https://delhihighcourt.nic.in/",
        "https://delhihighcourt.nic.in/case_status.php"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for url in urls_to_test:
        try:
            print(f"\nTesting URL: {url}")
            
            # Test basic connection
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check for CAPTCHA
                has_captcha = 'captcha' in response.text.lower() or 'verify' in response.text.lower()
                print(f"Has CAPTCHA: {has_captcha}")
                
                # Check page title
                title = soup.find('title')
                title_text = title.get_text(strip=True) if title else 'No title found'
                print(f"Page Title: {title_text}")
                
                # Look for forms
                forms = soup.find_all('form')
                print(f"Number of forms found: {len(forms)}")
                
                # Look for input fields
                inputs = soup.find_all('input')
                print(f"Number of input fields: {len(inputs)}")
                
                # Check if page contains case search functionality
                has_case_search = 'case' in response.text.lower() and 'search' in response.text.lower()
                print(f"Has case search functionality: {has_case_search}")
                
                # Check for specific case-related keywords
                case_keywords = ['writ petition', 'civil', 'criminal', 'appeal', 'case number']
                found_keywords = [kw for kw in case_keywords if kw in response.text.lower()]
                print(f"Found case keywords: {found_keywords}")
                
                # Save a sample of the HTML for inspection
                with open(f'delhi_high_court_{urls_to_test.index(url)}.html', 'w', encoding='utf-8') as f:
                    f.write(response.text[:5000])  # First 5000 characters
                print(f"Saved sample HTML to 'delhi_high_court_{urls_to_test.index(url)}.html'")
                
                return url
                
            else:
                print(f"Failed to access website. Status code: {response.status_code}")
                
        except Exception as e:
            print(f"Error testing website: {e}")
    
    return None

if __name__ == "__main__":
    working_url = test_delhi_high_court()
    if working_url:
        print(f"\n✅ Found working URL: {working_url}")
    else:
        print("\n❌ No working URLs found. The Delhi High Court website may be down or changed.") 