# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2024-01-XX

### Added
- HTML entity decoding functionality to fix display issues with `&nbsp;` and other HTML entities
- Custom Jinja2 filter `decode_html` for template-level entity decoding
- Helper method `_decode_html_entities` in scraper for data extraction level decoding
- Comprehensive application of HTML entity decoding to all relevant fields in results template
- New startup scripts (`run.py`, `run.bat`, `run.sh`) for easier application launching
- Updated documentation with troubleshooting section and recent updates
- Enhanced environment configuration with additional options

### Fixed
- **Critical Bug**: HTML entities like `&nbsp;` were being displayed as literal text instead of spaces
- Improved data extraction with proper HTML entity handling
- Updated requirements.txt with proper dependency documentation
- Enhanced environment variable configuration

### Changed
- Updated README.md with comprehensive documentation of the HTML entity fix
- Improved installation instructions and troubleshooting guide
- Enhanced environment example file with additional configuration options
- Updated project structure documentation

### Technical Details
- Added `html.unescape()` calls in data extraction methods
- Implemented custom Jinja2 filter for template-level entity decoding
- Applied decoding to case status, filing dates, party names, and order details
- Enhanced error handling for HTML processing

## [1.0.0] - Initial Release

### Added
- Flask web application for Delhi High Court case data fetching
- Web scraping functionality with BeautifulSoup4
- SQLite database for storing queries and responses
- PDF download functionality
- Responsive Bootstrap UI
- CAPTCHA solving with Tesseract OCR
- Session management and request handling
- Error handling and validation
- Search history tracking
- RESTful API endpoints

### Features
- Case search by type, number, and filing year
- Real-time data fetching from Delhi High Court portal
- PDF order/judgment downloads
- Search history and analytics
- Mobile-responsive design
- Comprehensive error handling 