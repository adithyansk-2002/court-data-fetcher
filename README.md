# Court Data Fetcher

A web application that fetches and displays case metadata and orders/judgments from the Delhi High Court portal with proper HTML entity handling.

## Features

- **Simple Web Interface**: Form with dropdowns for Case Type, Case Number, and Filing Year
- **Case Data Fetching**: Programmatically retrieves case information from Delhi High Court
- **Data Parsing**: Extracts parties' names, filing dates, next hearing dates, and order/judgment PDF links
- **HTML Entity Handling**: Properly decodes HTML entities (like `&nbsp;`) in displayed data
- **Database Storage**: Logs all queries and responses in SQLite database
- **PDF Downloads**: Allows downloading of linked PDFs
- **Error Handling**: User-friendly error messages for invalid cases or site issues
- **Responsive Design**: Modern, mobile-friendly UI with Bootstrap
- **Search History**: Tracks and displays recent searches

## Recent Updates

### HTML Entity Decoding Fix
- **Issue**: HTML entities like `&nbsp;` were being displayed as literal text instead of spaces
- **Solution**: Implemented comprehensive HTML entity decoding at both data extraction and template levels
- **Implementation**: 
  - Added `html.unescape()` in scraper data extraction
  - Created custom Jinja2 filter `decode_html` for template rendering
  - Applied decoding to all relevant fields in the results template

## Technical Approach

### CAPTCHA Strategy
The Delhi High Court portal uses session-based validation rather than traditional CAPTCHAs. Our approach:
1. **Session Management**: Maintains session cookies across requests
2. **Request Headers**: Uses realistic browser headers to avoid detection
3. **Rate Limiting**: Implements delays between requests to avoid being blocked
4. **Fallback Handling**: Graceful degradation when site is unavailable

### Technology Stack
- **Backend**: Python 3.9+ with Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla) with Bootstrap
- **Database**: SQLite (easily switchable to PostgreSQL)
- **Web Scraping**: Requests + BeautifulSoup4
- **PDF Handling**: PyPDF2 for metadata extraction
- **Image Processing**: OpenCV + Tesseract OCR for CAPTCHA solving
- **HTML Processing**: Built-in `html` module for entity decoding

## Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Tesseract OCR (for CAPTCHA solving)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd court-data-fetcher-test
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env with your configuration
   # (See env.example for available options)
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:5000`

### Environment Variables (.env)

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///court_data.db

# Scraping Configuration
REQUEST_DELAY=2
MAX_RETRIES=3
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# File Storage
UPLOAD_FOLDER=static/downloads
MAX_CONTENT_LENGTH=16777216

# Court Portal URLs
DELHI_HIGH_COURT_BASE_URL=https://delhihighcourt.nic.in
CASE_STATUS_URL=https://delhihighcourt.nic.in/case_status
```

## Usage

1. **Select Case Type**: Choose from available case types (e.g., Civil, Criminal, Writ Petition)
2. **Enter Case Number**: Input the specific case number
3. **Select Filing Year**: Choose the year when the case was filed
4. **Submit**: Click "Fetch Case Data" to retrieve information
5. **View Results**: Case details, parties, dates, and PDF links will be displayed with proper formatting
6. **Download PDFs**: Click on PDF links to download orders/judgments

## Project Structure

```
court-data-fetcher-test/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization
├── requirements.txt      # Python dependencies
├── env.example          # Environment variables template
├── README.md            # This file
├── static/              # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── downloads/       # Downloaded PDFs
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   └── results.html
├── models/              # Database models
│   └── database.py
├── scrapers/            # Web scraping modules
│   └── delhi_high_court_simple.py
└── utils/               # Utility functions
    ├── pdf_handler.py
    └── validators.py
```

## API Endpoints

- `GET /` - Main application page
- `POST /fetch-case` - Fetch case data
- `GET /download/<filename>` - Download PDF files
- `GET /api/case-types` - Get available case types
- `GET /api/search-history` - Get search history
- `GET /api/portal-status` - Check portal accessibility

## Database Schema

### Queries Table
- `id` (Primary Key)
- `case_type` (Text)
- `case_number` (Text)
- `filing_year` (Integer)
- `query_timestamp` (DateTime)
- `response_data` (JSON)
- `status` (Text)

### Downloads Table
- `id` (Primary Key)
- `query_id` (Foreign Key)
- `pdf_url` (Text)
- `local_path` (Text)
- `download_timestamp` (DateTime)

## Error Handling

The application handles various error scenarios:
- **Invalid Case Numbers**: Clear error messages for non-existent cases
- **Site Downtime**: Graceful handling when court portal is unavailable
- **Network Issues**: Retry mechanisms with exponential backoff
- **Invalid Input**: Form validation with helpful error messages
- **HTML Entity Issues**: Proper decoding of special characters

## Security Considerations

- **Input Validation**: All user inputs are validated and sanitized
- **SQL Injection Prevention**: Uses parameterized queries
- **File Upload Security**: Validates file types and sizes
- **Session Security**: Secure session management
- **No Hard-coded Secrets**: All sensitive data in environment variables

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Deployment

### Docker Deployment
```bash
# Build the Docker image
docker build -t court-data-fetcher .

# Run the container
docker run -p 5000:5000 court-data-fetcher
```

### Production Deployment
1. Set `FLASK_ENV=production`
2. Use a production WSGI server (Gunicorn)
3. Set up a reverse proxy (Nginx)
4. Configure SSL certificates
5. Use PostgreSQL for production database

## Troubleshooting

### Common Issues

1. **HTML entities showing as text**: This has been fixed with the latest update. If you still see issues, ensure you're running the latest version.

2. **Tesseract not found**: Install Tesseract OCR:
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

3. **Database errors**: Run `python init_db.py` to initialize the database.

4. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This application is for educational and research purposes only. Users are responsible for complying with the terms of service of the Delhi High Court website and applicable laws. The developers are not responsible for any misuse of this application. 