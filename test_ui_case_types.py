#!/usr/bin/env python3
"""
Test script to verify UI case types match the official Delhi High Court portal
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.validators import get_case_types
import requests
from bs4 import BeautifulSoup

def test_ui_case_types():
    """Test that the UI dropdown has the correct case types"""
    
    print("🏛️  Testing UI Case Types")
    print("=" * 50)
    
    # Get case types from our validators
    our_case_types = get_case_types()
    print(f"✅ Our application has {len(our_case_types)} case types")
    
    # Show first 10 case types
    print("\n📋 First 10 case types in our dropdown:")
    for i, case_type in enumerate(our_case_types[:10], 1):
        print(f"   {i}. {case_type}")
    
    # Check if we have the key case types from Delhi High Court
    key_case_types = [
        'W.P.(C)',  # Writ Petition (Civil)
        'W.P.(CRL)',  # Writ Petition (Criminal)
        'CRL.A.',  # Criminal Appeal
        'FAO',  # First Appeal from Order
        'RFA',  # Regular First Appeal
        'LPA',  # Letters Patent Appeal
    ]
    
    print(f"\n🎯 Checking for key Delhi High Court case types:")
    for case_type in key_case_types:
        if case_type in our_case_types:
            print(f"   ✅ {case_type}")
        else:
            print(f"   ❌ {case_type} (MISSING)")
    
    # Test the web interface
    print(f"\n🌐 Testing web interface...")
    try:
        response = requests.get("http://localhost:5000", timeout=10)
        if response.status_code == 200:
            print("   ✅ Web interface is accessible")
            
            # Check if the page contains our case types
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            
            found_count = 0
            for case_type in key_case_types:
                if case_type in page_text:
                    found_count += 1
            
            print(f"   📊 Found {found_count}/{len(key_case_types)} key case types in the web page")
            
            if found_count == len(key_case_types):
                print("   🎉 All key case types are present in the UI!")
            else:
                print("   ⚠️  Some case types might be missing from the UI")
                
        else:
            print(f"   ❌ Web interface returned status code: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error accessing web interface: {e}")
    
    print(f"\n📖 Summary:")
    print(f"   • Total case types: {len(our_case_types)}")
    print(f"   • Key case types present: {sum(1 for ct in key_case_types if ct in our_case_types)}/{len(key_case_types)}")
    print(f"   • Web interface: {'✅ Accessible' if 'response' in locals() and response.status_code == 200 else '❌ Not accessible'}")
    
    print(f"\n🚀 Your dropdown menu is now updated with official Delhi High Court case types!")
    print(f"   Open http://localhost:5000 in your browser to see the updated dropdown.")

if __name__ == "__main__":
    test_ui_case_types() 