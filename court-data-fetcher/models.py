from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class CourtCase(db.Model):
    """
    Model for storing court case information
    """
    __tablename__ = 'court_cases'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_number = db.Column(db.String(100), nullable=False, index=True)
    petitioner = db.Column(db.String(500), nullable=True)
    respondent = db.Column(db.String(500), nullable=True)
    filing_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(100), nullable=True)
    court = db.Column(db.String(100), nullable=False, default='Delhi High Court')
    case_type = db.Column(db.String(50), nullable=True)
    judge = db.Column(db.String(200), nullable=True)
    next_hearing = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CourtCase {self.case_number}>'
    
    def to_dict(self):
        """Convert case to dictionary"""
        return {
            'id': self.id,
            'case_number': self.case_number,
            'petitioner': self.petitioner,
            'respondent': self.respondent,
            'filing_date': self.filing_date.isoformat() if self.filing_date else None,
            'status': self.status,
            'court': self.court,
            'case_type': self.case_type,
            'judge': self.judge,
            'next_hearing': self.next_hearing.isoformat() if self.next_hearing else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SearchLog(db.Model):
    """
    Model for logging search queries
    """
    __tablename__ = 'search_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    search_type = db.Column(db.String(20), nullable=False)  # 'case_number' or 'party_name'
    search_query = db.Column(db.String(500), nullable=False)
    results_count = db.Column(db.Integer, default=0)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SearchLog {self.search_type}: {self.search_query}>'

class CaseUpdate(db.Model):
    """
    Model for tracking case updates
    """
    __tablename__ = 'case_updates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = db.Column(db.String(36), db.ForeignKey('court_cases.id'), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    case = db.relationship('CourtCase', backref=db.backref('updates', lazy=True))
    
    def __repr__(self):
        return f'<CaseUpdate {self.case_id}: {self.field_name}>'

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create indexes for better performance
        db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_case_number ON court_cases(case_number)'))
        db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_petitioner ON court_cases(petitioner)'))
        db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_respondent ON court_cases(respondent)'))
        db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_filing_date ON court_cases(filing_date)'))
        db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_status ON court_cases(status)'))
        db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_created_at ON court_cases(created_at)'))
        db.session.commit()

def log_search(search_type: str, search_query: str, results_count: int, 
               ip_address: str = None, user_agent: str = None):
    """Log a search query"""
    try:
        log_entry = SearchLog(
            search_type=search_type,
            search_query=search_query,
            results_count=results_count,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging search: {e}")

def get_case_by_number(case_number: str):
    """Get case by case number"""
    return CourtCase.query.filter_by(case_number=case_number).first()

def search_cases_by_party(party_name: str, limit: int = 10):
    """Search cases by party name"""
    return CourtCase.query.filter(
        (CourtCase.petitioner.ilike(f'%{party_name}%')) |
        (CourtCase.respondent.ilike(f'%{party_name}%'))
    ).limit(limit).all()

def search_cases_by_number(case_number: str, limit: int = 10):
    """Search cases by case number"""
    return CourtCase.query.filter(
        CourtCase.case_number.ilike(f'%{case_number}%')
    ).limit(limit).all()

def add_case(case_data: dict):
    """Add a new case to the database"""
    try:
        case = CourtCase(**case_data)
        db.session.add(case)
        db.session.commit()
        return case
    except Exception as e:
        db.session.rollback()
        print(f"Error adding case: {e}")
        return None
    finally:
        # Ensure session is properly closed in case of errors
        if db.session.is_active:
            db.session.close()

def update_case(case_id: str, update_data: dict):
    """Update an existing case"""
    try:
        case = CourtCase.query.get(case_id)
        if not case:
            return None
        
        # Track changes
        for field, new_value in update_data.items():
            if hasattr(case, field):
                old_value = getattr(case, field)
                if old_value != new_value:
                    # Log the update
                    update_log = CaseUpdate(
                        case_id=case_id,
                        field_name=field,
                        old_value=str(old_value) if old_value else None,
                        new_value=str(new_value) if new_value else None
                    )
                    db.session.add(update_log)
                    
                    # Update the field
                    setattr(case, field, new_value)
        
        db.session.commit()
        return case
    except Exception as e:
        db.session.rollback()
        print(f"Error updating case: {e}")
        return None

def get_recent_cases(limit: int = 10):
    """Get recent cases"""
    return CourtCase.query.order_by(CourtCase.created_at.desc()).limit(limit).all()

def get_cases_by_status(status: str, limit: int = 10):
    """Get cases by status"""
    return CourtCase.query.filter_by(status=status).limit(limit).all()

def get_cases_by_date_range(start_date, end_date, limit: int = 10):
    """Get cases filed within a date range"""
    return CourtCase.query.filter(
        CourtCase.filing_date >= start_date,
        CourtCase.filing_date <= end_date
    ).limit(limit).all()

def get_search_statistics():
    """Get search statistics"""
    total_cases = CourtCase.query.count()
    total_searches = SearchLog.query.count()
    
    # Get search counts by type
    case_number_searches = SearchLog.query.filter_by(search_type='case_number').count()
    party_name_searches = SearchLog.query.filter_by(search_type='party_name').count()
    
    return {
        'total_cases': total_cases,
        'total_searches': total_searches,
        'case_number_searches': case_number_searches,
        'party_name_searches': party_name_searches
    }
