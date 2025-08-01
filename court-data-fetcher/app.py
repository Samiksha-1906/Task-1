from flask import Flask, render_template, request, jsonify
from models import CourtCase, db
from scraper.delhi_high_court import DelhiHighCourtScraper
from utils import format_date, validate_case_number
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    """Main page for the court data fetcher"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_cases():
    """Search for court cases"""
    try:
        data = request.get_json()
        case_number = data.get('case_number', '').strip()
        party_name = data.get('party_name', '').strip()
        
        if not case_number and not party_name:
            return jsonify({'error': 'Please provide either case number or party name'}), 400
        
        # Validate case number if provided
        if case_number and not validate_case_number(case_number):
            return jsonify({'error': 'Invalid case number format'}), 400
        
        # Search in database first
        query = CourtCase.query
        
        if case_number:
            query = query.filter(CourtCase.case_number.ilike(f'%{case_number}%'))
        if party_name:
            query = query.filter(
                (CourtCase.petitioner.ilike(f'%{party_name}%')) |
                (CourtCase.respondent.ilike(f'%{party_name}%'))
            )
        
        existing_cases = query.limit(10).all()
        
        # If no results in database, try scraping
        if not existing_cases:
            scraper = DelhiHighCourtScraper()
            scraped_cases = scraper.search_cases(case_number, party_name)
            
            if scraped_cases:
                # Save scraped cases to database
                try:
                    for case_data in scraped_cases:
                        case = CourtCase(**case_data)
                        db.session.add(case)
                    db.session.commit()
                    
                    return jsonify({'cases': scraped_cases})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error saving scraped cases: {e}")
                    # Return scraped cases even if database save fails
                    return jsonify({'cases': scraped_cases})
            else:
                return jsonify({'cases': [], 'message': 'No cases found'})
        
        # Return existing cases from database
        cases = []
        for case in existing_cases:
            cases.append({
                'case_number': case.case_number,
                'petitioner': case.petitioner,
                'respondent': case.respondent,
                'filing_date': format_date(case.filing_date),
                'status': case.status,
                'court': case.court
            })
        
        return jsonify({'cases': cases})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/case/<case_number>')
def get_case_details(case_number):
    """Get detailed information about a specific case"""
    try:
        case = CourtCase.query.filter_by(case_number=case_number).first()
        
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        case_data = {
            'case_number': case.case_number,
            'petitioner': case.petitioner,
            'respondent': case.respondent,
            'filing_date': format_date(case.filing_date),
            'status': case.status,
            'court': case.court,
            'case_type': case.case_type,
            'judge': case.judge,
            'next_hearing': format_date(case.next_hearing) if case.next_hearing else None
        }
        
        return jsonify(case_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint to verify database connectivity"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/test-scraper')
def test_scraper():
    """Test the scraper connection to Delhi High Court"""
    try:
        scraper = DelhiHighCourtScraper()
        test_result = scraper.test_connection()
        
        return jsonify({
            'scraper_test': test_result,
            'message': 'Scraper test completed'
        })
        
    except Exception as e:
        logger.error(f"Error testing scraper: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Scraper test failed'
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
