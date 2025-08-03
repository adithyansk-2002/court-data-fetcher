#!/usr/bin/env python3
"""
Test script to demonstrate searching with real case numbers
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.delhi_high_court_simple import DelhiHighCourtSimpleScraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_real_case_search():
    """Test searching with real case numbers"""
    
    print("🏛️  Testing Real Case Search with Delhi High Court")
    print("=" * 60)
    
    # Load real cases
    try:
        with open('real_cases.json', 'r') as f:
            real_cases = json.load(f)
    except FileNotFoundError:
        print("❌ real_cases.json not found. Run find_real_cases.py first.")
        return
    
    # Initialize scraper
    scraper = DelhiHighCourtSimpleScraper()
    
    # Test with first few real cases
    test_cases = real_cases[:3]  # Test first 3 cases
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: Searching for Case {case['case_number']}/{case['filing_year']}")
        print("-" * 50)
        
        # Use a common case type since we don't have specific types
        case_type = "WP(C)"  # Most common type - Writ Petition (Civil)
        
        try:
            # Search for the case
            result = scraper.search_case(case_type, case['case_number'], case['filing_year'])
            
            if result['status'] == 'success':
                case_data = result['case_data']
                print(f"✅ Search successful!")
                print(f"   Case ID: {case_data.get('case_id', 'N/A')}")
                print(f"   Petitioners: {len(case_data.get('petitioners', []))}")
                print(f"   Respondents: {len(case_data.get('respondents', []))}")
                print(f"   Filing Date: {case_data.get('filing_date', 'N/A')}")
                print(f"   Next Hearing: {case_data.get('next_hearing_date', 'N/A')}")
                print(f"   Orders/PDFs: {len(case_data.get('orders', []))}")
                
                # Check if we got real data or mock data
                if case_data.get('case_id') and not case_data['case_id'].startswith('CivilWritPetition'):
                    print("   🎯 REAL DATA FOUND!")
                else:
                    print("   📝 Using mock data (no real case found)")
                    
            else:
                print(f"❌ Search failed: {result['error_message']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎯 Summary:")
    print(f"   • Tested {len(test_cases)} real case numbers")
    print(f"   • Real case numbers found: {len(real_cases)}")
    print(f"   • You can use any of these in your web application!")

def show_usage_instructions():
    """Show how to use real case numbers in the web app"""
    
    print("\n📖 How to Use Real Case Numbers in Your Web App:")
    print("=" * 60)
    
    try:
        with open('real_cases.json', 'r') as f:
            real_cases = json.load(f)
        
        print("1. Open your browser and go to: http://localhost:5000")
        print("2. Use these real case numbers:")
        
        for i, case in enumerate(real_cases[:5], 1):
            print(f"   {i}. Case Number: {case['case_number']}")
            print(f"      Filing Year: {case['filing_year']}")
            print(f"      Case Type: WP(C) (recommended)")
            print()
        
        print("3. Example search:")
        if real_cases:
            example = real_cases[0]
            print(f"   • Case Type: WP(C)")
            print(f"   • Case Number: {example['case_number']}")
            print(f"   • Filing Year: {example['filing_year']}")
        
        print("\n4. The application will:")
        print("   • Connect to Delhi High Court portal")
        print("   • Search for the case")
        print("   • Display results (real data if found, mock data otherwise)")
        print("   • Show PDF links if available")
        
    except FileNotFoundError:
        print("❌ real_cases.json not found. Run find_real_cases.py first.")

if __name__ == "__main__":
    test_real_case_search()
    show_usage_instructions() 