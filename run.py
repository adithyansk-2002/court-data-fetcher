#!/usr/bin/env python3
"""
Simple startup script for Court Data Fetcher
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """Start the Flask application"""
    
    # Load environment variables
    load_dotenv()
    
    # Set default values if not in environment
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('DEBUG', 'True')
    os.environ.setdefault('HOST', '127.0.0.1')
    os.environ.setdefault('PORT', '5000')
    
    # Import and run the app
    try:
        from app import create_app
        app = create_app()
        
        host = os.environ.get('HOST', '127.0.0.1')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'True').lower() == 'true'
        
        print(f"Starting Court Data Fetcher on {host}:{port}")
        print(f"Debug mode: {debug}")
        print(f"Access the application at: http://{host}:{port}")
        print("Press Ctrl+C to stop the application")
        
        app.run(host=host, port=port, debug=debug)
        
    except ImportError as e:
        print(f"Error importing application: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 