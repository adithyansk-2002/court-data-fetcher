#!/usr/bin/env python3
"""
Test script for the enhanced Delhi High Court scraper with real portal access
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.delhi_high_court import DelhiHighCourtScraper
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_portal_access():
    """Test if we can access the Delhi High Court portal"""
    print("🔍 Testing Delhi High Court Portal Access...")
    
    scraper = DelhiHighCourtScraper(use_selenium=False)  # Start with requests only
    
    # Test portal accessibility
    status = scraper.get_portal_status()
    print(f"Portal Status: {status}")
    
    if status['accessible']:
        print("✅ Portal is accessible!")
        
        # Try to get the case status page
        soup = scraper.get_case_status_page()
        if soup:
            print("✅ Successfully retrieved case status page")
            
            # Look for search forms
            form_info = scraper.find_search_form(soup)
            if form_info:
                print(f"✅ Found search form: {form_info['action']}")
            else:
                print("⚠️  No search form found on the page")
                
            # Look for CAPTCHA
            captcha_data = scraper.get_captcha_image(soup)
            if captcha_data:
                print("✅ CAPTCHA detected on the page")
                
                # Test CAPTCHA solving
                captcha_text = scraper.solve_captcha(captcha_data)
                if captcha_text:
                    print(f"✅ CAPTCHA solved: {captcha_text}")
                else:
                    print("❌ Failed to solve CAPTCHA")
            else:
                print("ℹ️  No CAPTCHA detected")
        else:
            print("❌ Failed to retrieve case status page")
    else:
        print("❌ Portal is not accessible")
        print(f"Error: {status.get('error', 'Unknown error')}")

def test_selenium_scraper():
    """Test Selenium-based scraper"""
    print("\n🤖 Testing Selenium-based Scraper...")
    
    try:
        scraper = DelhiHighCourtScraper(use_selenium=True)
        
        # Test Selenium driver setup
        driver = scraper.setup_selenium_driver()
        if driver:
            print("✅ Selenium driver setup successful")
            
            # Test navigation to portal
            try:
                driver.get(scraper.base_url)
                print("✅ Successfully navigated to Delhi High Court portal")
                
                # Get page title
                title = driver.title
                print(f"Page Title: {title}")
                
                # Look for case search elements
                search_elements = driver.find_elements("xpath", "//a[contains(text(), 'Case') or contains(text(), 'Search') or contains(text(), 'Status')]")
                if search_elements:
                    print(f"✅ Found {len(search_elements)} potential search links")
                    for i, elem in enumerate(search_elements[:3]):  # Show first 3
                        print(f"  {i+1}. {elem.text}")
                else:
                    print("⚠️  No search links found")
                    
            except Exception as e:
                print(f"❌ Error during Selenium navigation: {e}")
                
        else:
            print("❌ Failed to setup Selenium driver")
            
    except Exception as e:
        print(f"❌ Error in Selenium test: {e}")

def test_captcha_solving():
    """Test CAPTCHA solving with a sample image"""
    print("\n🔐 Testing CAPTCHA Solving...")
    
    scraper = DelhiHighCourtScraper()
    
    # Create a simple test image with text
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Create a test image with text
        img = Image.new('RGB', (200, 80), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        # Add some text
        text = "ABC123"
        draw.text((20, 20), text, fill='black', font=font)
        
        # Convert to bytes
        from io import BytesIO
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()
        
        # Test CAPTCHA solving
        solved_text = scraper.solve_captcha(img_data)
        print(f"Original text: {text}")
        print(f"Solved text: {solved_text}")
        
        if solved_text:
            print("✅ CAPTCHA solving test successful")
        else:
            print("❌ CAPTCHA solving test failed")
            
    except Exception as e:
        print(f"❌ Error in CAPTCHA test: {e}")

def test_real_case_search():
    """Test a real case search (will use mock data if portal is not accessible)"""
    print("\n📋 Testing Real Case Search...")
    
    scraper = DelhiHighCourtScraper(use_selenium=True)
    
    # Test with sample case data
    case_type = "Civil Writ Petition"
    case_number = "1234"
    filing_year = 2023
    
    print(f"Searching for: {case_type} {case_number}/{filing_year}")
    
    try:
        result = scraper.search_case(case_type, case_number, filing_year)
        
        if result['status'] == 'success':
            print("✅ Case search successful!")
            case_data = result['case_data']
            
            print(f"Case ID: {case_data.get('case_id', 'N/A')}")
            print(f"Petitioners: {', '.join(case_data.get('petitioners', []))}")
            print(f"Respondents: {', '.join(case_data.get('respondents', []))}")
            print(f"Filing Date: {case_data.get('filing_date', 'N/A')}")
            print(f"Next Hearing: {case_data.get('next_hearing_date', 'N/A')}")
            print(f"Status: {case_data.get('case_status', 'N/A')}")
            print(f"Orders/PDFs: {len(case_data.get('orders', []))}")
            
        else:
            print(f"❌ Case search failed: {result['error_message']}")
            
    except Exception as e:
        print(f"❌ Error in case search: {e}")

if __name__ == "__main__":
    print("🚀 Testing Enhanced Delhi High Court Scraper")
    print("=" * 50)
    
    # Test portal access
    test_portal_access()
    
    # Test Selenium scraper
    test_selenium_scraper()
    
    # Test CAPTCHA solving
    test_captcha_solving()
    
    # Test real case search
    test_real_case_search()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!") 