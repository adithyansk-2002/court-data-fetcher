# Quick Start Guide - Court Data Fetcher

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Step 1: Clone and Setup
```bash
# Navigate to the project directory
cd court-data-fetcher-test

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
# Initialize the database
python init_db.py

# Optional: Add sample data
python init_db.py --sample-data
```

### Step 3: Run the Application
```bash
# Option 1: Use the startup script (recommended)
python start.py

# Option 2: Run directly
python app.py
```

### Step 4: Access the Application
Open your browser and go to: **http://localhost:5000**

## 🐳 Docker Quick Start

### Using Docker Compose (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at: http://localhost:5000
```

### Using Docker directly
```bash
# Build the image
docker build -t court-data-fetcher .

# Run the container
docker run -p 5000:5000 court-data-fetcher

# Access at: http://localhost:5000
```

## 📋 What You Can Do

1. **Search Cases**: Enter case type, number, and filing year
2. **View Results**: See case details, parties, and dates
3. **Download PDFs**: Get orders and judgments
4. **View History**: Check your search history
5. **API Access**: Use REST endpoints for integration

## 🔧 Configuration

### Environment Variables
Copy `env.example` to `.env` and modify:
```bash
cp env.example .env
```

Key settings:
- `SECRET_KEY`: Change for production
- `DATABASE_URL`: Database connection string
- `DEBUG`: Set to False for production

### Database
- **Development**: SQLite (default)
- **Production**: PostgreSQL recommended

## 🧪 Testing

Run the test suite:
```bash
# Install pytest if not already installed
pip install pytest

# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## 📁 Project Structure

```
court-data-fetcher-test/
├── app.py                 # Main Flask application
├── start.py              # Startup script
├── init_db.py            # Database initialization
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── README.md            # Full documentation
├── QUICK_START.md       # This file
├── static/              # Static files (CSS, JS, downloads)
├── templates/           # HTML templates
├── models/              # Database models
├── scrapers/            # Web scraping modules
├── utils/               # Utility functions
└── tests/               # Test files
```

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in .env file
   PORT=5001
   ```

2. **Database errors**
   ```bash
   # Reinitialize database
   python init_db.py
   ```

3. **Import errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **Permission errors (Linux/Mac)**
   ```bash
   # Fix permissions
   chmod +x start.py
   chmod +x init_db.py
   ```

### Getting Help

1. Check the full [README.md](README.md) for detailed documentation
2. Review error messages in the console
3. Check the logs in the `logs/` directory
4. Ensure all dependencies are installed correctly

## 🎯 Next Steps

1. **Customize**: Modify the scraper for your specific court
2. **Deploy**: Use Docker for production deployment
3. **Extend**: Add more features like email notifications
4. **Monitor**: Set up logging and monitoring
5. **Secure**: Configure SSL certificates for HTTPS

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the full documentation in README.md
3. Check the test files for usage examples
4. Ensure you're using the correct Python version

---

**Happy Court Data Fetching! 🏛️** 