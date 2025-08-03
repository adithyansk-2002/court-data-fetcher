from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Query(db.Model):
    """Model for storing case search queries and responses"""
    __tablename__ = 'queries'
    
    id = db.Column(db.Integer, primary_key=True)
    case_type = db.Column(db.String(100), nullable=False)
    case_number = db.Column(db.String(100), nullable=False)
    filing_year = db.Column(db.Integer, nullable=False)
    query_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    response_data = db.Column(db.Text)  # JSON string
    status = db.Column(db.String(50), default='pending')  # pending, success, error
    error_message = db.Column(db.Text)
    
    # Relationship with downloads
    downloads = db.relationship('Download', backref='query', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Query {self.case_type}/{self.case_number}/{self.filing_year}>'
    
    def to_dict(self):
        """Convert query to dictionary"""
        return {
            'id': self.id,
            'case_type': self.case_type,
            'case_number': self.case_number,
            'filing_year': self.filing_year,
            'query_timestamp': self.query_timestamp.isoformat() if self.query_timestamp else None,
            'response_data': json.loads(self.response_data) if self.response_data else None,
            'status': self.status,
            'error_message': self.error_message
        }
    
    def set_response_data(self, data):
        """Set response data as JSON string"""
        self.response_data = json.dumps(data, default=str)

class Download(db.Model):
    """Model for storing downloaded PDF files"""
    __tablename__ = 'downloads'
    
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('queries.id'), nullable=False)
    pdf_url = db.Column(db.String(500), nullable=False)
    local_path = db.Column(db.String(500), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    download_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)  # in bytes
    status = db.Column(db.String(50), default='pending')  # pending, success, error
    
    def __repr__(self):
        return f'<Download {self.filename}>'
    
    def to_dict(self):
        """Convert download to dictionary"""
        return {
            'id': self.id,
            'query_id': self.query_id,
            'pdf_url': self.pdf_url,
            'local_path': self.local_path,
            'filename': self.filename,
            'download_timestamp': self.download_timestamp.isoformat() if self.download_timestamp else None,
            'file_size': self.file_size,
            'status': self.status
        }

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!") 