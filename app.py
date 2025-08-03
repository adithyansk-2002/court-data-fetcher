from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from datetime import datetime
from urllib.parse import unquote
import json
import html

# Import our modules
from models.database import db, Query, Download, init_db
from scrapers.delhi_high_court_simple import DelhiHighCourtSimpleScraper as DelhiHighCourtScraper
from utils.validators import validate_form_data, sanitize_input, get_case_types, get_year_range
from utils.pdf_handler import PDFHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///court_data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'static/downloads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # Initialize extensions
    init_db(app)
    
    # Add custom Jinja2 filters
    @app.template_filter('decode_html')
    def decode_html_entities(text):
        """Decode HTML entities in template"""
        if not text:
            return ''
        return html.unescape(str(text))
    
    # Initialize scrapers and handlers
    scraper = DelhiHighCourtScraper()
    pdf_handler = PDFHandler(app.config['UPLOAD_FOLDER'])
    
    # Routes
    @app.route('/')
    def index():
        """Main page with search form"""
        try:
            # Get recent searches for display
            recent_searches = Query.query.order_by(Query.query_timestamp.desc()).limit(5).all()
            
            return render_template('index.html', 
                                case_types=get_case_types(),
                                year_range=get_year_range(),
                                recent_searches=recent_searches)
        except Exception as e:
            logger.error(f"Error in index route: {str(e)}")
            flash('An error occurred while loading the page', 'error')
            return render_template('index.html', 
                                case_types=get_case_types(),
                                year_range=get_year_range(),
                                recent_searches=[])

    @app.route('/fetch-case', methods=['POST'])
    def fetch_case():
        """Handle case search request"""
        try:
            # Get form data
            case_type = request.form.get('case_type', '').strip()
            case_number = request.form.get('case_number', '').strip()
            filing_year = request.form.get('filing_year', '').strip()
            
            # Sanitize inputs
            case_type = sanitize_input(case_type)
            case_number = sanitize_input(case_number)
            
            # Validate inputs
            try:
                filing_year = int(filing_year)
            except (ValueError, TypeError):
                flash('Invalid filing year', 'error')
                return redirect(url_for('index'))
            
            # Validate form data
            is_valid, error_message = validate_form_data(case_type, case_number, filing_year)
            if not is_valid:
                flash(error_message, 'error')
                return redirect(url_for('index'))
            
            # Create query record
            query = Query(
                case_type=case_type,
                case_number=case_number,
                filing_year=filing_year,
                status='pending'
            )
            db.session.add(query)
            db.session.commit()
            
            # Search for case data
            search_result = scraper.search_case(case_type, case_number, filing_year)
            
            if search_result['status'] == 'success':
                # Update query with success status
                query.status = 'success'
                query.set_response_data(search_result['case_data'])
                db.session.commit()
                
                # Render results page
                return render_template('results.html', 
                                    case_data=search_result['case_data'],
                                    query=query)
            else:
                # Update query with error status
                query.status = 'error'
                query.error_message = search_result['error_message']
                db.session.commit()
                
                flash(f'Error fetching case data: {search_result["error_message"]}', 'error')
                return redirect(url_for('index'))
                
        except Exception as e:
            logger.error(f"Error in fetch_case route: {str(e)}")
            flash('An unexpected error occurred while fetching case data', 'error')
            return redirect(url_for('index'))

    @app.route('/download/<path:url>')
    def download_pdf(url):
        """Download PDF file"""
        try:
            # Decode the URL
            pdf_url = unquote(url)
            
            # Download the PDF
            download_result = pdf_handler.download_pdf(pdf_url)
            
            if download_result['status'] == 'success':
                # Create download record
                download = Download(
                    query_id=request.args.get('query_id', type=int),
                    pdf_url=pdf_url,
                    local_path=download_result['local_path'],
                    filename=download_result['filename'],
                    file_size=download_result['file_size'],
                    status='success'
                )
                db.session.add(download)
                db.session.commit()
                
                # Send the file
                return send_file(download_result['local_path'], 
                               as_attachment=True,
                               download_name=download_result['filename'])
            else:
                flash(f'Error downloading PDF: {download_result["error_message"]}', 'error')
                return redirect(request.referrer or url_for('index'))
                
        except Exception as e:
            logger.error(f"Error in download_pdf route: {str(e)}")
            flash('An error occurred while downloading the PDF', 'error')
            return redirect(request.referrer or url_for('index'))

    @app.route('/search-history')
    def search_history():
        """Display search history"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = 20
            
            queries = Query.query.order_by(Query.query_timestamp.desc()).paginate(
                page=page, per_page=per_page, error_out=False)
            
            return render_template('search_history.html', queries=queries)
        except Exception as e:
            logger.error(f"Error in search_history route: {str(e)}")
            flash('An error occurred while loading search history', 'error')
            return redirect(url_for('index'))

    @app.route('/api/case-types')
    def api_case_types():
        """API endpoint to get case types"""
        try:
            return jsonify({
                'status': 'success',
                'case_types': get_case_types()
            })
        except Exception as e:
            logger.error(f"Error in api_case_types: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch case types'
            }), 500

    @app.route('/api/search-history')
    def api_search_history():
        """API endpoint to get search history"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            queries = Query.query.order_by(Query.query_timestamp.desc()).paginate(
                page=page, per_page=per_page, error_out=False)
            
            history = []
            for query in queries.items:
                history.append({
                    'id': query.id,
                    'case_type': query.case_type,
                    'case_number': query.case_number,
                    'filing_year': query.filing_year,
                    'status': query.status,
                    'timestamp': query.query_timestamp.isoformat() if query.query_timestamp else None
                })
            
            return jsonify({
                'status': 'success',
                'history': history,
                'total': queries.total,
                'pages': queries.pages,
                'current_page': queries.page
            })
        except Exception as e:
            logger.error(f"Error in api_search_history: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch search history'
            }), 500

    @app.route('/api/portal-status')
    def api_portal_status():
        """API endpoint to check portal status"""
        try:
            status = scraper.get_portal_status()
            return jsonify({
                'status': 'success',
                'portal_status': status
            })
        except Exception as e:
            logger.error(f"Error in api_portal_status: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to check portal status'
            }), 500

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    
    # Get configuration from environment
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting Court Data Fetcher on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    app.run(host=host, port=port, debug=debug) 