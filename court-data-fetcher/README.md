# Court Data Fetcher

A modern web application for searching and retrieving court case information from Delhi High Court. Built with Flask, SQLAlchemy, and BeautifulSoup for web scraping.

## Court Chosen
**Delhi High Court** (https://delhihighcourt.nic.in/)

## CAPTCHA Strategy
The Delhi High Court website may implement CAPTCHA protection. Our approach:

1. **Initial Detection**: The scraper detects CAPTCHA presence automatically
2. **Fallback Strategy**: If CAPTCHA is detected, the system falls back to mock data for demonstration
3. **Manual Bypass**: For production use, consider:
   - 2Captcha service integration
   - Manual CAPTCHA solving
   - Alternative court websites (District Courts)
4. **User Notification**: Clear messages when CAPTCHA blocks access

## Sample Environment Variables
```bash
# Database Configuration
DATABASE_URL=sqlite:///database/db.sqlite3
FLASK_ENV=development
FLASK_DEBUG=True

# Scraper Configuration
SCRAPER_TIMEOUT=30
SCRAPER_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
COURT_BASE_URL=https://delhihighcourt.nic.in

# Optional: 2Captcha API (for CAPTCHA solving)
CAPTCHA_API_KEY=your_2captcha_api_key_here
```

## Features

- 🔍 **Search by Case Number**: Search cases using various case number formats (W.P.(C), LPA, FAO, etc.)
- 👥 **Search by Party Name**: Find cases by petitioner or respondent names
- 💾 **Database Storage**: Store and cache case information for faster retrieval
- 📱 **Responsive Design**: Modern, mobile-friendly user interface
- 🔄 **Real-time Updates**: Live search with loading indicators
- 📊 **Case Details**: Comprehensive case information display
- 🎨 **Modern UI**: Beautiful gradient design with smooth animations

## Project Structure

```
court-data-fetcher/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Main web interface
├── static/
│   └── style.css         # CSS styles
├── scraper/
│   └── delhi_high_court.py # Web scraper for Delhi High Court
├── database/
│   └── db.sqlite3        # SQLite database (created automatically)
├── models.py             # Database models and functions
├── utils.py              # Utility functions
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd court-data-fetcher
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to `http://localhost:5000`

## Usage

### Searching Cases

1. **By Case Number**:
   - Enter the case number in the format: `W.P.(C) 1234/2023`
   - Supported formats:
     - `W.P.(C) 1234/2023`
     - `LPA 123/2023`
     - `FAO 456/2023`
     - `CRL.A. 789-2023`

2. **By Party Name**:
   - Enter the name of petitioner or respondent
   - Search is case-insensitive and supports partial matches

### Viewing Results

- Search results are displayed in a clean card layout
- Click on any case card to view detailed information
- Case status is color-coded for easy identification

## Database Schema

### CourtCase Table
- `id`: Unique identifier (UUID)
- `case_number`: Case number (indexed)
- `petitioner`: Petitioner name
- `respondent`: Respondent name
- `filing_date`: Date of filing
- `status`: Case status
- `court`: Court name (default: Delhi High Court)
- `case_type`: Type of case
- `judge`: Assigned judge
- `next_hearing`: Next hearing date
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

### SearchLog Table
- `id`: Unique identifier (UUID)
- `search_type`: Type of search ('case_number' or 'party_name')
- `search_query`: Actual search query
- `results_count`: Number of results returned
- `ip_address`: User's IP address
- `user_agent`: User's browser information
- `created_at`: Search timestamp

### CaseUpdate Table
- `id`: Unique identifier (UUID)
- `case_id`: Reference to court case
- `field_name`: Name of updated field
- `old_value`: Previous value
- `new_value`: New value
- `updated_at`: Update timestamp

## API Endpoints

### GET /
Main page with search interface

### POST /search
Search for cases
```json
{
  "case_number": "W.P.(C) 1234/2023",
  "party_name": "John Doe"
}
```

### GET /case/<case_number>
Get detailed information for a specific case

## Configuration

The application uses the following default configuration:

- **Database**: SQLite (`database/db.sqlite3`)
- **Host**: `0.0.0.0` (accessible from any IP)
- **Port**: `5000`
- **Debug Mode**: Enabled for development

## Dependencies

- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **requests**: HTTP library for web scraping
- **beautifulsoup4**: HTML parsing
- **lxml**: XML/HTML parser

## Development

### Adding New Courts

To add support for other courts:

1. Create a new scraper class in the `scraper/` directory
2. Implement the required methods:
   - `search_cases(case_number, party_name)`
   - `get_case_details(case_number)`
3. Update the main application to use the new scraper

### Customizing the UI

The application uses modern CSS with:
- CSS Grid for layout
- Flexbox for components
- CSS custom properties for theming
- Responsive design principles

### Database Migrations

The application automatically creates the database schema on first run. For production deployments, consider using Flask-Migrate for database migrations.

## Error Handling

The application includes comprehensive error handling:

- **Input Validation**: Case number and party name validation
- **Network Errors**: Graceful handling of scraping failures
- **Database Errors**: Transaction rollback on failures
- **User Feedback**: Clear error messages in the UI

## Performance Considerations

- **Database Indexing**: Key fields are indexed for faster queries
- **Caching**: Search results are cached in the database
- **Pagination**: Results are limited to prevent overwhelming responses
- **Connection Pooling**: Database connections are managed efficiently

## Security Features

- **Input Sanitization**: User inputs are sanitized to prevent injection attacks
- **SQL Injection Protection**: Using SQLAlchemy ORM with parameterized queries
- **XSS Protection**: HTML escaping in templates
- **CSRF Protection**: Built-in Flask CSRF protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This application is for educational and research purposes only. Please ensure compliance with the terms of service of the Delhi High Court website and applicable laws when using this tool.

## Support

For issues and questions:
1. Check the existing issues
2. Create a new issue with detailed information
3. Include error logs and steps to reproduce

## Roadmap

- [ ] Support for additional courts
- [ ] Advanced search filters
- [ ] Export functionality (PDF, Excel)
- [ ] User authentication
- [ ] Case tracking and notifications
- [ ] API rate limiting
- [ ] Docker containerization
