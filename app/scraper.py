# app/scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
import pytesseract
from PIL import Image
import requests
import base64
from io import BytesIO
from bs4 import BeautifulSoup

# Configure path to Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Change if different

def solve_captcha(driver):
    # Find CAPTCHA image as base64
    img_element = driver.find_element(By.ID, 'captcha_image')
    src = img_element.get_attribute('src')

    # Some courts use base64-encoded images
    if "base64," in src:
        base64_data = src.split("base64,")[1]
        img_data = base64.b64decode(base64_data)
        image = Image.open(BytesIO(img_data))
    else:
        img_url = src
        response = requests.get(img_url, stream=True)
        image = Image.open(response.raw)

    # OCR the image
    captcha_text = pytesseract.image_to_string(image).strip()
    captcha_text = ''.join(filter(str.isalnum, captcha_text))  # Clean it up
    return captcha_text

def scrape_case_details(case_type, case_number, filing_year):
    options = Options()
    options.add_argument('--headless')  # Remove this line if you want to see the browser for debugging
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index"
        driver.get(url)
        time.sleep(2)

        # --- 1. Select State: Delhi ---
        state_dropdown = Select(driver.find_element(By.ID, "sess_state_code"))
        state_dropdown.select_by_visible_text("Delhi")
        time.sleep(2)

        # --- 2. Select District: Central ---
        district_dropdown = Select(driver.find_element(By.ID, "sess_district_code"))
        district_dropdown.select_by_visible_text("Central")
        time.sleep(2)

        # --- 3. Select Court Complex: Tis Hazari Courts ---
        court_dropdown = Select(driver.find_element(By.ID, "court_complex_code"))
        court_dropdown.select_by_visible_text("Tis Hazari Courts, Delhi")
        time.sleep(2)

        # --- 4. Select Case Type ---
        case_type_dropdown = Select(driver.find_element(By.ID, "case_type_code"))
        case_type_dropdown.select_by_visible_text(case_type)
        time.sleep(1)

        # --- 5. Enter Case Number & Year ---
        driver.find_element(By.ID, "case_no").send_keys(case_number)
        driver.find_element(By.ID, "case_year").send_keys(filing_year)

        # --- 6. Solve CAPTCHA ---
        captcha_text = solve_captcha(driver)
        driver.find_element(By.ID, "captcha_code").send_keys(captcha_text)
        time.sleep(1)

        # --- 7. Submit Form ---
        driver.find_element(By.ID, "searchbtn").click()
        time.sleep(3)

        # --- 8. Grab HTML + return dummy result for now ---
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        result = {
            "case_type": case_type,
            "case_number": case_number,
            "filing_year": filing_year,
            "parties": "Petitioner vs Respondent",
            "filing_date": "2022-01-01",
            "next_hearing": "2025-09-10",
            "latest_order_link": "https://example.com/fake.pdf",
            "raw_html": html
        }

        return result

    finally:
        driver.quit()

