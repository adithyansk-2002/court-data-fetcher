#!/usr/bin/env python3
"""
Database initialization script for Court Data Fetcher
"""

import os
import sys
from flask import Flask
from models.database import init_db, db

def create_app():
    """Create a minimal Flask app for database operations"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///court_data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    return app

def init_database():
    """Initialize the database"""
    try:
        app = create_app()
        
        with app.app_context():
            # Initialize database
            init_db(app)
            
            print("✅ Database initialized successfully!")
            print(f"📁 Database file: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Check if tables were created
            from models.database import Query, Download
            
            # Test database connection
            try:
                # Try to query the tables
                query_count = Query.query.count()
                download_count = Download.query.count()
                
                print(f"📊 Queries table: {query_count} records")
                print(f"📊 Downloads table: {download_count} records")
                print("✅ Database connection test successful!")
                
            except Exception as e:
                print(f"⚠️  Database connection test failed: {str(e)}")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        app = create_app()
        
        with app.app_context():
            from models.database import Query, Download
            from datetime import datetime
            
            # Check if sample data already exists
            if Query.query.count() > 0:
                print("ℹ️  Sample data already exists, skipping...")
                return True
            
            # Create sample queries
            sample_queries = [
                {
                    'case_type': 'Civil',
                    'case_number': '123/2023',
                    'filing_year': 2023,
                    'status': 'success',
                    'response_data': {
                        'case_id': 'Civil/123/2023',
                        'petitioners': ['Sample Petitioner'],
                        'respondents': ['Sample Respondent'],
                        'filing_date': '2023-01-15',
                        'next_hearing_date': '2024-02-15',
                        'case_status': 'Pending'
                    }
                },
                {
                    'case_type': 'Criminal',
                    'case_number': '456/2022',
                    'filing_year': 2022,
                    'status': 'success',
                    'response_data': {
                        'case_id': 'Criminal/456/2022',
                        'petitioners': ['State of Delhi'],
                        'respondents': ['Accused Person'],
                        'filing_date': '2022-06-20',
                        'next_hearing_date': '2024-01-30',
                        'case_status': 'Pending'
                    }
                },
                {
                    'case_type': 'Writ Petition',
                    'case_number': '789/2021',
                    'filing_year': 2021,
                    'status': 'error',
                    'error_message': 'Case not found in database'
                }
            ]
            
            for query_data in sample_queries:
                query = Query(
                    case_type=query_data['case_type'],
                    case_number=query_data['case_number'],
                    filing_year=query_data['filing_year'],
                    status=query_data['status'],
                    query_timestamp=datetime.now()
                )
                
                if query_data['status'] == 'success':
                    query.set_response_data(query_data['response_data'])
                else:
                    query.error_message = query_data['error_message']
                
                db.session.add(query)
            
            db.session.commit()
            
            print("✅ Sample data created successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        return False

def main():
    """Main function"""
    print("🏛️  Court Data Fetcher - Database Initialization")
    print("=" * 50)
    
    # Initialize database
    if not init_database():
        print("❌ Database initialization failed!")
        sys.exit(1)
    
    # Ask if user wants sample data
    if len(sys.argv) > 1 and sys.argv[1] == '--sample-data':
        print("\n📝 Creating sample data...")
        if create_sample_data():
            print("✅ Sample data created!")
        else:
            print("❌ Failed to create sample data!")
    
    print("\n🎉 Database setup complete!")
    print("\nNext steps:")
    print("1. Run 'python app.py' to start the application")
    print("2. Open http://localhost:5000 in your browser")
    print("3. Start searching for court cases!")

if __name__ == '__main__':
    main() 