# Installation Guide

This guide will help you install and run the Court Data Fetcher application.

## Prerequisites

### Required Software
- **Python 3.9 or higher**
  - Download from [python.org](https://www.python.org/downloads/)
  - Make sure to check "Add Python to PATH" during installation

- **Tesseract OCR** (for CAPTCHA solving)
  - **Windows**: Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
  - **macOS**: `brew install tesseract`
  - **Linux**: `sudo apt-get install tesseract-ocr`

### Optional Software
- **Git** (for cloning the repository)
- **Virtual Environment** (recommended)

## Installation Methods

### Method 1: Quick Start (Windows)

1. **Download and extract** the project files
2. **Double-click** `run.bat` to automatically:
   - Create virtual environment
   - Install dependencies
   - Initialize database
   - Start the application

### Method 2: Quick Start (Linux/macOS)

1. **Download and extract** the project files
2. **Make the script executable** (if needed):
   ```bash
   chmod +x run.sh
   ```
3. **Run the script**:
   ```bash
   ./run.sh
   ```

### Method 3: Manual Installation

#### Step 1: Clone or Download
```bash
# If using Git
git clone <repository-url>
cd court-data-fetcher-test

# Or download and extract the ZIP file
```

#### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your settings (optional)
# The defaults should work for most users
```

#### Step 5: Initialize Database
```bash
python init_db.py
```

#### Step 6: Run the Application
```bash
# Option 1: Use the startup script
python run.py

# Option 2: Run directly
python app.py
```

## Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=True
HOST=127.0.0.1
PORT=5000

# Database Configuration
DATABASE_URL=sqlite:///court_data.db

# Scraping Configuration
REQUEST_DELAY=2
MAX_RETRIES=3
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# File Storage
UPLOAD_FOLDER=static/downloads
MAX_CONTENT_LENGTH=16777216

# OCR Configuration (for CAPTCHA solving)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Logging Configuration
LOG_LEVEL=INFO
```

### Tesseract Configuration

**Windows:**
- Install Tesseract from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- Update `TESSERACT_CMD` in `.env` if installed elsewhere

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

## Verification

After installation, you should be able to:

1. **Start the application** without errors
2. **Access the web interface** at `http://127.0.0.1:5000`
3. **See the search form** with case type dropdowns
4. **Perform test searches** (though real data depends on court portal availability)

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

#### 2. "Tesseract not found" errors
- **Windows**: Install Tesseract from the provided link
- **macOS/Linux**: Install via package manager
- Update `TESSERACT_CMD` path in `.env` if needed

#### 3. Database errors
```bash
# Solution: Initialize database
python init_db.py
```

#### 4. Port already in use
```bash
# Solution: Change port in .env file
PORT=5001
```

#### 5. Permission errors (Linux/macOS)
```bash
# Solution: Make scripts executable
chmod +x run.sh
```

### Getting Help

If you encounter issues:

1. **Check the logs** in the terminal output
2. **Verify prerequisites** are installed correctly
3. **Try the troubleshooting section** in README.md
4. **Check the CHANGELOG.md** for known issues

## Next Steps

After successful installation:

1. **Access the application** at `http://127.0.0.1:5000`
2. **Try a test search** with sample case data
3. **Explore the features** like search history and PDF downloads
4. **Read the README.md** for detailed usage instructions

## Development Setup

For developers who want to contribute:

1. **Fork the repository**
2. **Create a feature branch**
3. **Install in development mode**:
   ```bash
   pip install -e .
   ```
4. **Run tests**:
   ```bash
   python -m pytest tests/
   ```
5. **Make your changes** and submit a pull request 