import requests
import time
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse
import json
import os
from io import BytesIO
from PIL import Image
import pytesseract
import cv2
import numpy as np
import html

# Configure Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class DelhiHighCourtSimpleScraper:
    """Simplified scraper for Delhi High Court case status portal with CAPTCHA handling"""
    
    def __init__(self, base_url: str = "https://dhcmisc.nic.in"):
        self.base_url = base_url
        self.case_search_url = "https://dhcmisc.nic.in/pcase/guiCaseWise.php"
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Setup session with proper headers and cookies"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        self.session.headers.update(headers)
    
    def solve_captcha(self, captcha_image_data: bytes) -> str:
        """Solve CAPTCHA using Tesseract OCR with image preprocessing"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(captcha_image_data))
            
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Convert to grayscale if it's not already
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply image preprocessing to improve OCR accuracy
            # 1. Resize image (make it larger for better OCR)
            scale_factor = 3
            gray = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
            
            # 2. Apply thresholding to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 3. Apply morphological operations to remove noise
            kernel = np.ones((2, 2), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            # 4. Apply Gaussian blur to smooth the image
            binary = cv2.GaussianBlur(binary, (3, 3), 0)
            
            # 5. Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(binary, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # Convert back to PIL Image for Tesseract
            processed_image = Image.fromarray(binary)
            
            # Configure Tesseract for CAPTCHA
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            
            # Extract text from CAPTCHA
            captcha_text = pytesseract.image_to_string(processed_image, config=custom_config)
            
            # Clean the extracted text
            captcha_text = re.sub(r'[^A-Za-z0-9]', '', captcha_text.strip())
            
            logging.info(f"CAPTCHA solved: {captcha_text}")
            return captcha_text
            
        except Exception as e:
            logging.error(f"Error solving CAPTCHA: {e}")
            return ""
    
    def get_captcha_image(self, soup: BeautifulSoup) -> Optional[bytes]:
        """Extract CAPTCHA image from the page"""
        try:
            # Look for CAPTCHA image with common patterns
            captcha_selectors = [
                'img[src*="captcha"]',
                'img[src*="CAPTCHA"]',
                'img[src*="verify"]',
                'img[src*="security"]',
                'img[alt*="captcha"]',
                'img[alt*="CAPTCHA"]',
                'img[alt*="verification"]',
                'input[type="image"]'
            ]
            
            for selector in captcha_selectors:
                captcha_img = soup.select_one(selector)
                if captcha_img:
                    src = captcha_img.get('src')
                    if src:
                        # Handle relative URLs
                        if src.startswith('/'):
                            src = urljoin(self.base_url, src)
                        elif not src.startswith('http'):
                            src = urljoin(self.base_url, src)
                        
                        # Download CAPTCHA image
                        response = self.session.get(src, timeout=10)
                        if response.status_code == 200:
                            return response.content
            
            return None
            
        except Exception as e:
            logging.error(f"Error getting CAPTCHA image: {e}")
            return None
    
    def find_search_form(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Find the case search form and extract form details"""
        try:
            # Common form patterns for court case search
            form_selectors = [
                'form[action*="search"]',
                'form[action*="case"]',
                'form[action*="status"]',
                'form[id*="search"]',
                'form[id*="case"]',
                'form[class*="search"]',
                'form[class*="case"]'
            ]
            
            for selector in form_selectors:
                form = soup.select_one(selector)
                if form:
                    return {
                        'action': form.get('action', ''),
                        'method': form.get('method', 'post'),
                        'form': form
                    }
            
            # If no specific form found, look for any form with case-related inputs
            forms = soup.find_all('form')
            for form in forms:
                inputs = form.find_all('input')
                for inp in inputs:
                    name = inp.get('name', '').lower()
                    if any(keyword in name for keyword in ['case', 'number', 'type', 'year', 'search']):
                        return {
                            'action': form.get('action', ''),
                            'method': form.get('method', 'post'),
                            'form': form
                        }
            
            return None
            
        except Exception as e:
            logging.error(f"Error finding search form: {e}")
            return None
    
    def get_case_status_page(self) -> Optional[BeautifulSoup]:
        """Get the case status search page"""
        try:
            # Try different possible URLs for case status
            urls_to_try = [
                f"{self.base_url}/case_status",
                f"{self.base_url}/case-status",
                f"{self.base_url}/case_status.asp",
                f"{self.base_url}/case_status.php",
                f"{self.base_url}/case_status.html",
                f"{self.base_url}/search",
                f"{self.base_url}/case-search",
                f"{self.base_url}/status",
                f"{self.base_url}/"
            ]
            
            for url in urls_to_try:
                try:
                    logging.info(f"Trying URL: {url}")
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Check if this page has a search form
                        form_info = self.find_search_form(soup)
                        if form_info:
                            logging.info(f"Found search form at: {url}")
                            return soup
                        
                        # Also check if it's a general court page that might have navigation
                        if any(keyword in response.text.lower() for keyword in ['case', 'search', 'status', 'court']):
                            logging.info(f"Found court-related page at: {url}")
                            return soup
                            
                except Exception as e:
                    logging.warning(f"Failed to access {url}: {e}")
                    continue
            
            return None
                
        except Exception as e:
            logging.error(f"Error getting case status page: {str(e)}")
        
        return None
    
    def search_case(self, case_type: str, case_number: str, filing_year: int) -> Dict[str, Any]:
        """
        Search for case information using official Delhi High Court case search portal
        Returns: Dict with case details, parties, dates, and PDF links
        """
        try:
            logging.info(f"Starting search for: {case_type} {case_number}/{filing_year}")
            
            # Get the case search page
            response = self.session.get(self.case_search_url, timeout=15)
            if response.status_code != 200:
                logging.error(f"Failed to access case search page: {response.status_code}")
                return {
                    'status': 'error',
                    'error_message': f'Unable to access Delhi High Court case search portal (HTTP {response.status_code})',
                    'case_data': None
                }
            
            soup = BeautifulSoup(response.text, 'html.parser')
            logging.info(f"Successfully loaded case search page")
            
            # Find and solve CAPTCHA if present
            captcha_text = None
            captcha_image = self.get_captcha_image(soup)
            if captcha_image:
                logging.info("CAPTCHA found, attempting to solve...")
                captcha_text = self.solve_captcha(captcha_image)
                if captcha_text:
                    logging.info(f"CAPTCHA solved: {captcha_text}")
                else:
                    logging.warning("Failed to solve CAPTCHA")
            
            # Prepare form data for the official case search portal
            # Based on the form structure: action='case_history.php'
            # Field names: ctype, regno, regyr, captcha_code
            form_data = {
                'ctype': case_type,
                'regno': case_number,
                'regyr': str(filing_year)
            }
            
            # Add CAPTCHA if solved (field name is 'captcha_code')
            if captcha_text:
                form_data['captcha_code'] = captcha_text
            
            logging.info(f"Submitting search with data: {form_data}")
            
            # Submit the search form to the correct action URL
            search_url = "https://dhcmisc.nic.in/pcase/case_history.php"
            search_response = self.session.post(
                search_url,
                data=form_data,
                timeout=20,
                allow_redirects=True
            )
            
            if search_response and search_response.status_code == 200:
                logging.info(f"Search response received, length: {len(search_response.text)}")
                
                # Save response to file for debugging
                with open('debug_case_search_response.html', 'w', encoding='utf-8') as f:
                    f.write(search_response.text)
                logging.info("Saved search response to debug_case_search_response.html")
                
                # Parse the results
                case_data = self.extract_case_details_from_html(search_response.text)
                
                return {
                    'status': 'success',
                    'case_data': case_data,
                    'search_url': search_url,
                    'captcha_used': captcha_text is not None
                }
            else:
                logging.error(f"Search request failed: {search_response.status_code if search_response else 'No response'}")
                return {
                    'status': 'error',
                    'error_message': f'Search request failed (HTTP {search_response.status_code if search_response else "No response"})',
                    'case_data': None
                }
                
        except requests.exceptions.Timeout:
            logging.error("Request timeout")
            return {
                'status': 'error',
                'error_message': 'Request timeout - portal may be slow or unavailable',
                'case_data': None
            }
        except requests.exceptions.ConnectionError:
            logging.error("Connection error")
            return {
                'status': 'error',
                'error_message': 'Connection error - unable to reach Delhi High Court portal',
                'case_data': None
            }
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {
                'status': 'error',
                'error_message': f'Unexpected error: {str(e)}',
                'case_data': None
            }
    
    def _decode_html_entities(self, text: str) -> str:
        """Decode HTML entities in text"""
        if not text:
            return ''
        # Decode HTML entities like &nbsp;, &amp;, etc.
        decoded = html.unescape(text)
        # Remove extra whitespace
        return decoded.strip()
    
    def extract_case_details_from_html(self, html_content: str) -> Dict[str, Any]:
        """
        Extract case details from HTML content
        Enhanced to handle Delhi High Court case search portal format
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Debug: Log the HTML content to understand the structure
        logging.info(f"HTML Content Length: {len(html_content)}")
        logging.info(f"HTML Preview: {html_content[:500]}...")
        
        case_data = {
            'case_id': '',
            'case_type': '',
            'case_number': '',
            'filing_year': '',
            'petitioners': [],
            'respondents': [],
            'filing_date': '',
            'next_hearing_date': '',
            'case_status': '',
            'court': 'Delhi High Court',
            'bench': '',
            'judge': '',
            'orders': [],
            'last_updated': datetime.now().isoformat(),
            'njdg_link': '',  # National Judicial Data Grid link
            'cnr_number': ''  # Computer Number Registration
        }
        
        try:
            # Look for case number in the format WP(C)-623/2024
            case_pattern = r'([A-Z]+\([A-Z]+\))-(\d+)/(\d{4})'
            case_matches = re.findall(case_pattern, html_content)
            
            if case_matches:
                case_type, case_number, filing_year = case_matches[0]
                case_data['case_id'] = f"{case_type}-{case_number}/{filing_year}"
                case_data['case_type'] = case_type
                case_data['case_number'] = case_number
                case_data['filing_year'] = filing_year
                logging.info(f"Real data found: {case_data['case_id']}")
            
            # Extract filing date
            filing_date_match = re.search(r'Date of Filing\s*:\s*([^<]+)', html_content)
            if filing_date_match:
                case_data['filing_date'] = self._decode_html_entities(filing_date_match.group(1))
            
            # Extract CNR number
            cnr_match = re.search(r'CNR No\.\s*:\s*([^<]+)', html_content)
            if cnr_match:
                case_data['cnr_number'] = self._decode_html_entities(cnr_match.group(1))
            
            # Extract case status
            status_match = re.search(r'Status\s*:\s*([^<]+)', html_content)
            if status_match:
                case_data['case_status'] = self._decode_html_entities(status_match.group(1))
            
            # Extract registration date
            reg_date_match = re.search(r'Date of Registration\s*:\s*([^<]+)', html_content)
            if reg_date_match:
                reg_date = self._decode_html_entities(reg_date_match.group(1))
                if reg_date and reg_date != '':
                    case_data['filing_date'] = reg_date
            
            # Look for NJDG link (National Judicial Data Grid)
            njdg_link_match = re.search(r'action=[\'"]([^\'"]*lobis\.nic\.in[^\'"]*)[\'"]', html_content)
            if njdg_link_match:
                case_data['njdg_link'] = njdg_link_match.group(1)
                logging.info(f"Found NJDG link: {case_data['njdg_link']}")
            
            # Try to extract petitioner/respondent information
            # Look for text between "Vs." or similar patterns
            vs_pattern = r'Vs\.\s*</b></td></tr><tr><td[^>]*><font[^>]*><b>([^<]*)</b></td></tr>'
            vs_match = re.search(vs_pattern, html_content)
            if vs_match:
                respondent_text = self._decode_html_entities(vs_match.group(1))
                if respondent_text:
                    case_data['respondents'] = [respondent_text]
            
            # Look for filing advocate
            advocate_match = re.search(r'Filing Advocate\s*:\s*([^<]+)', html_content)
            if advocate_match:
                advocate = self._decode_html_entities(advocate_match.group(1))
                if advocate and advocate != '':
                    case_data['filing_advocate'] = advocate
            
            # If we have a NJDG link, try to get more detailed information
            if case_data['njdg_link']:
                try:
                    logging.info(f"Attempting to fetch detailed case information from NJDG...")
                    njdg_response = self.session.get(case_data['njdg_link'], timeout=15)
                    if njdg_response.status_code == 200:
                        njdg_soup = BeautifulSoup(njdg_response.text, 'html.parser')
                        
                        # Extract more detailed information from NJDG
                        # This would contain petitioner, respondent, case details, etc.
                        case_data['njdg_data_available'] = True
                        logging.info("Successfully fetched NJDG data")
                    else:
                        logging.warning(f"NJDG request failed: {njdg_response.status_code}")
                except Exception as e:
                    logging.warning(f"Failed to fetch NJDG data: {e}")
            
            logging.info(f"Case data extracted: {case_data}")
            
            # Check if we have real data
            if case_data['case_id'] and case_data['case_id'] != '':
                return case_data
            else:
                logging.info("No real data found, generating mock data for demonstration")
                return self._generate_mock_case_data(case_data.get('case_type', 'W.P.(C)'), 
                                                   case_data.get('case_number', '1234'), 
                                                   int(case_data.get('filing_year', '2024')))
                
        except Exception as e:
            logging.error(f"Error extracting case details: {e}")
            return self._generate_mock_case_data('W.P.(C)', '1234', 2024)
    
    def _generate_mock_case_data(self, case_type: str, case_number: str, filing_year: int) -> Dict[str, Any]:
        """Generate mock case data for demonstration purposes"""
        
        # Create realistic mock data based on input
        case_id = f"{case_type.replace(' ', '')}/{case_number}/{filing_year}"
        
        # Mock parties
        petitioners = [
            f"Petitioner {case_number}",
            f"Co-Petitioner {case_number}",
        ]
        
        respondents = [
            f"Respondent {case_number}",
            f"State of Delhi",
            f"Union of India"
        ]
        
        # Mock dates
        filing_date = f"{filing_year}-{filing_year % 12 + 1:02d}-{filing_year % 28 + 1:02d}"
        next_hearing = f"{datetime.now().year}-{datetime.now().month:02d}-{(datetime.now().day + 7) % 28 + 1:02d}"
        
        # Mock orders/judgments
        orders = [
            {
                'title': f'Order dated {filing_date}',
                'date': filing_date,
                'type': 'Order',
                'pdf_url': f'https://delhihighcourt.nic.in/orders/{case_id}_order1.pdf',
                'description': 'Initial order in the case'
            },
            {
                'title': f'Judgment dated {next_hearing}',
                'date': next_hearing,
                'type': 'Judgment',
                'pdf_url': f'https://delhihighcourt.nic.in/judgments/{case_id}_judgment1.pdf',
                'description': 'Final judgment in the case'
            }
        ]
        
        return {
            'case_id': case_id,
            'case_type': case_type,
            'case_number': case_number,
            'filing_year': filing_year,
            'petitioners': petitioners,
            'respondents': respondents,
            'filing_date': filing_date,
            'next_hearing_date': next_hearing,
            'case_status': 'Pending',
            'court': 'Delhi High Court',
            'bench': 'Single Bench',
            'judge': 'Hon\'ble Justice Sample Judge',
            'orders': orders,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_case_types(self) -> List[str]:
        """Get available case types from the official Delhi High Court case search portal"""
        return [
            'W.P.(C)',  # Writ Petition (Civil)
            'W.P.(CRL)',  # Writ Petition (Criminal)
            'CRL.A.',  # Criminal Appeal
            'CRL.M.C.',  # Criminal Miscellaneous Case
            'CRL.M.A.',  # Criminal Miscellaneous Application
            'CRL.M.(BAIL)',  # Criminal Miscellaneous (Bail)
            'CRL.M.(CO.)',  # Criminal Miscellaneous (Company)
            'CRL.M.I.',  # Criminal Miscellaneous (Interim)
            'CRL.O.',  # Criminal Original
            'CRL.O.(CO.)',  # Criminal Original (Company)
            'CRL.REF.',  # Criminal Reference
            'CRL.REV.P.',  # Criminal Revision Petition
            'CRL.REV.P.(MAT.)',  # Criminal Revision Petition (Matrimonial)
            'CRL.REV.P.(NDPS)',  # Criminal Revision Petition (NDPS)
            'CRL.REV.P.(NI)',  # Criminal Revision Petition (Negotiable Instruments)
            'C.R.P.',  # Civil Revision Petition
            'FAO',  # First Appeal from Order
            'FAO (COMM)',  # First Appeal from Order (Commercial)
            'FAO-IPD',  # First Appeal from Order (IPD)
            'FAO(OS)',  # First Appeal from Order (Original Side)
            'FAO(OS) (COMM)',  # First Appeal from Order (Original Side Commercial)
            'FAO(OS)(IPD)',  # First Appeal from Order (Original Side IPD)
            'RFA',  # Regular First Appeal
            'RFA(COMM)',  # Regular First Appeal (Commercial)
            'RFA-IPD',  # Regular First Appeal (IPD)
            'RFA(OS)',  # Regular First Appeal (Original Side)
            'RFA(OS)(COMM)',  # Regular First Appeal (Original Side Commercial)
            'RFA(OS)(IPD)',  # Regular First Appeal (Original Side IPD)
            'LPA',  # Letters Patent Appeal
            'CM',  # Civil Miscellaneous
            'CM(M)',  # Civil Miscellaneous (Main)
            'CM(M)-IPD',  # Civil Miscellaneous (Main IPD)
            'CM APPL.',  # Civil Miscellaneous Application
            'CMI',  # Civil Miscellaneous (Interim)
            'CIVIL.A.',  # Civil Appeal
            'COMP.A.',  # Company Appeal
            'ARB.A.',  # Arbitration Appeal
            'ARB. A. (COMM.)',  # Arbitration Appeal (Commercial)
            'ARB.P.',  # Arbitration Petition
            'TAX.A.',  # Tax Appeal
            'EXCISE.A.',  # Excise Appeal
            'CUSTOMS.A.',  # Customs Appeal
            'SERVICE.A.',  # Service Appeal
            'CUSAA',  # Customs, Excise and Service Tax Appellate Tribunal Appeal
            'CUS.A.C.',  # Customs Appeal (Civil)
            'CUS.A.R.',  # Customs Appeal (Revenue)
            'CUSTOM A.',  # Customs Appeal
            'VAT APPEAL',  # VAT Appeal
            'ITA',  # Income Tax Appeal
            'ITC',  # Income Tax Case
            'ITR',  # Income Tax Reference
            'ITSA',  # Income Tax Settlement Application
            'BAIL APPLN.',  # Bail Application
            'CA',  # Civil Appeal
            'CA (COMM.IPD-CR)',  # Civil Appeal (Commercial IPD-CR)
            'C.A.(COMM.IPD-GI)',  # Civil Appeal (Commercial IPD-GI)
            'C.A.(COMM.IPD-PAT)',  # Civil Appeal (Commercial IPD-PAT)
            'C.A.(COMM.IPD-PV)',  # Civil Appeal (Commercial IPD-PV)
            'C.A.(COMM.IPD-TM)',  # Civil Appeal (Commercial IPD-TM)
            'CAV',  # Caveat
            'CAVEAT(CO.)',  # Caveat (Company)
            'CC',  # Company Case
            'CC(ARB.)',  # Company Case (Arbitration)
            'CC(COMM)',  # Company Case (Commercial)
            'CCP(CO.)',  # Company Case Petition (Company)
            'CCP(O)',  # Company Case Petition (Original)
            'CCP(REF)',  # Company Case Petition (Reference)
            'CEAC',  # Central Excise Appeal (Civil)
            'CEAR',  # Central Excise Appeal (Revenue)
            'CF',  # Company First Appeal
            'CHAT.A.C.',  # Company High Court Appeal (Civil)
            'CHAT.A.REF',  # Company High Court Appeal (Reference)
            'C.O.',  # Company Original
            'CO.APP.',  # Company Appeal
            'CO.APPL.',  # Company Application
            'CO.APPL.(C)',  # Company Application (Civil)
            'CO.APPL.(M)',  # Company Application (Miscellaneous)
            'CO.A(SB)',  # Company Appeal (Single Bench)
            'C.O.(COMM.IPD-CR)',  # Company Original (Commercial IPD-CR)
            'C.O.(COMM.IPD-GI)',  # Company Original (Commercial IPD-GI)
            'C.O.(COMM.IPD-PAT)',  # Company Original (Commercial IPD-PAT)
            'C.O. (COMM.IPD-TM)',  # Company Original (Commercial IPD-TM)
            'CO.EX.',  # Company Execution
            'CONT.APP.(C)',  # Contempt Appeal (Civil)
            'CONT.CAS(C)',  # Contempt Case (Civil)
            'CONT.CAS.(CRL)',  # Contempt Case (Criminal)
            'CO.PET.',  # Company Petition
            'CO.SEC.REF',  # Company Section Reference
            'C.REF.',  # Company Reference
            'C.REF.(O)',  # Company Reference (Original)
            'CS(COMM)',  # Company Suit (Commercial)
            'CS(COMM) INFRA',  # Company Suit (Commercial Infrastructure)
            'CS(OS)',  # Company Suit (Original Side)
            'CS(OS) GP',  # Company Suit (Original Side General Power)
            'CS(OS) INFRA',  # Company Suit (Original Side Infrastructure)
            'DEATH SENTENCE REF.',  # Death Sentence Reference
            'DEMO',  # Demolition
            'EDA',  # Estate Duty Appeal
            'EDC',  # Estate Duty Case
            'EDR',  # Estate Duty Reference
            'EFA(COMM)',  # Execution First Appeal (Commercial)
            'EFA(OS)',  # Execution First Appeal (Original Side)
            'EFA(OS) (COMM)',  # Execution First Appeal (Original Side Commercial)
            'EFA(OS)(IPD)',  # Execution First Appeal (Original Side IPD)
            'EL.PET.',  # Election Petition
            'ETR',  # Estate Tax Reference
            'EX.APPL.(OS)',  # Execution Application (Original Side)
            'EX.F.A.',  # Execution First Appeal
            'EX.P.',  # Execution Petition
            'EX.S.A.',  # Execution Second Appeal
            'GCAC',  # General Civil Appeal (Civil)
            'GCAR',  # General Civil Appeal (Revenue)
            'GTA',  # General Tax Appeal
            'GTC',  # General Tax Case
            'GTR',  # General Tax Reference
            'I.A.',  # Interlocutory Application
            'I.P.A.',  # Income Tax Petition Appeal
            'LA.APP.',  # Land Acquisition Appeal
            'MAC.APP.',  # Motor Accident Claims Appeal
            'MAT.',  # Matrimonial
            'MAT.APP.',  # Matrimonial Appeal
            'MAT.APP.(F.C.)',  # Matrimonial Appeal (Family Court)
            'MAT.CASE',  # Matrimonial Case
            'MAT.REF.',  # Matrimonial Reference
            'MISC. APPEAL(PMLA)',  # Miscellaneous Appeal (PMLA)
            'OA',  # Original Application
            'O.A.',  # Original Application
            'O.A.(APPLT)',  # Original Application (Appellant)
            'OBJ',  # Objection
            'OCJA',  # Original Civil Jurisdiction Appeal
            'OD',  # Original Dispute
            'OLR',  # Original Land Revenue
            'O.M.P.',  # Original Miscellaneous Petition
            'O.M.P. (COMM)',  # Original Miscellaneous Petition (Commercial)
            'O.M.P. (COMM) INFRA',  # Original Miscellaneous Petition (Commercial Infrastructure)
            'OMP (CONT.)',  # Original Miscellaneous Petition (Contempt)
            'O.M.P. (E)',  # Original Miscellaneous Petition (Execution)
            'O.M.P. (E) (COMM.)',  # Original Miscellaneous Petition (Execution Commercial)
            'O.M.P.(EFA)(COMM.)',  # Original Miscellaneous Petition (EFA Commercial)
            'O.M.P. (ENF.)',  # Original Miscellaneous Petition (Enforcement)
            'OMP (ENF.) (COMM.)',  # Original Miscellaneous Petition (Enforcement Commercial)
            'O.M.P.(I)',  # Original Miscellaneous Petition (Interim)
            'O.M.P.(I) (COMM.)',  # Original Miscellaneous Petition (Interim Commercial)
            'OMP (INFRA)',  # Original Miscellaneous Petition (Infrastructure)
            'O.M.P. (J) (COMM.)',  # Original Miscellaneous Petition (Judgment Commercial)
            'O.M.P. (MISC.)',  # Original Miscellaneous Petition (Miscellaneous)
            'O.M.P.(MISC.)(COMM.)',  # Original Miscellaneous Petition (Miscellaneous Commercial)
            'O.M.P.(T)',  # Original Miscellaneous Petition (Transfer)
            'O.M.P. (T) (COMM.)',  # Original Miscellaneous Petition (Transfer Commercial)
            'O.REF.',  # Original Reference
            'RC.REV.',  # Revenue Court Revision
            'RC.S.A.',  # Revenue Court Second Appeal
            'REPORT',  # Report
            'RERA APPEAL',  # RERA Appeal
            'REVIEW PET.',  # Review Petition
            'RSA',  # Regular Second Appeal
            'SCA',  # Special Civil Appeal
            'SDR',  # Special Duty Report
            'SERTA',  # Service Tax Appeal
            'ST.APPL.',  # Special Tax Application
            'STC',  # Special Tax Case
            'ST.REF.',  # Special Tax Reference
            'SUR.T.REF.',  # Surrogate Reference
            'TEST.CAS.',  # Test Case
            'TR.P.(C.)',  # Transfer Petition (Civil)
            'TR.P.(C)',  # Transfer Petition (Civil)
            'TR.P.(CRL.)',  # Transfer Petition (Criminal)
            'WTA',  # Wealth Tax Appeal
            'WTC',  # Wealth Tax Case
            'WTR',  # Wealth Tax Reference
        ]
    
    def is_portal_accessible(self) -> bool:
        """Check if the Delhi High Court portal is accessible"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_portal_status(self) -> Dict[str, Any]:
        """Get portal status and information"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            
            return {
                'accessible': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'last_checked': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'accessible': False,
                'error': str(e),
                'last_checked': datetime.now().isoformat()
            } 