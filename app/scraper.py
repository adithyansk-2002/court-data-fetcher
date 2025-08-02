# app/scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        url = "https://services.ecourts.gov.in/ecourtindia_v6/"
        driver.get(url)
        time.sleep(2)

        # Click on 'District Court' tab
        driver.find_element(By.LINK_TEXT, "District Courts").click()
        time.sleep(2)

        # Select Delhi → District: Central → Court Complex: Tis Hazari
        # (this may vary based on real court setup - adjust dropdowns if needed)

        # Select Case Status → Search by Case Number
        driver.find_element(By.LINK_TEXT, "Case Status").click()
        time.sleep(2)
        driver.find_element(By.LINK_TEXT, "Search by Case Number").click()
        time.sleep(2)

        # Fill in form fields
        driver.find_element(By.NAME, 'case_type').send_keys(case_type)
        driver.find_element(By.NAME, 'case_no').send_keys(case_number)
        driver.find_element(By.NAME, 'case_year').send_keys(filing_year)

        # Solve and enter CAPTCHA
        captcha = solve_captcha(driver)
        driver.find_element(By.NAME, 'captcha').send_keys(captcha)

        # Submit
        driver.find_element(By.ID, 'submit').click()
        time.sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Parse dummy data for now – update as needed once real HTML structure is confirmed
        result = {
            "case_type": case_type,
            "case_number": case_number,
            "filing_year": filing_year,
            "parties": "Petitioner vs Respondent",
            "filing_date": "2022-05-01",
            "next_hearing": "2025-09-10",
            "latest_order_link": "https://example.com/fakeorder.pdf",
            "raw_html": html
        }

        return result
    finally:
        driver.quit()
