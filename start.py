#!/usr/bin/env python3
"""
Startup script for Court Data Fetcher
Initializes database and starts the application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Error: Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import requests
        import beautifulsoup4
        import sqlalchemy
        print("✅ All required dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = [
        "static/downloads",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def initialize_database():
    """Initialize the database"""
    try:
        print("🔧 Initializing database...")
        result = subprocess.run([sys.executable, "init_db.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database initialized successfully")
        else:
            print(f"❌ Database initialization failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    
    return True

def start_application():
    """Start the Flask application"""
    print("🚀 Starting Court Data Fetcher...")
    
    # Set environment variables
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('DEBUG', 'True')
    
    try:
        # Import and run the app
        from app import create_app
        
        app = create_app()
        
        # Get configuration
        host = os.environ.get('HOST', '127.0.0.1')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'True').lower() == 'true'
        
        print(f"🌐 Application will be available at: http://{host}:{port}")
        print(f"🔧 Debug mode: {debug}")
        print("📁 Database: court_data.db")
        print("\n" + "="*50)
        print("🏛️  Court Data Fetcher is running!")
        print("="*50)
        print("\nPress Ctrl+C to stop the application")
        
        app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("🏛️  Court Data Fetcher - Startup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    check_dependencies()
    
    # Create directories
    create_directories()
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        sys.exit(1)
    
    # Start application
    start_application()

if __name__ == '__main__':
    main() 