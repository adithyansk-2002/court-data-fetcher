# app/main.py
from flask import Flask, render_template, request, redirect, url_for
from scraper import scrape_case_details
from db import init_db, log_query

app = Flask(__name__)
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch():
    case_type = request.form['case_type']
    case_number = request.form['case_number']
    filing_year = request.form['filing_year']

    try:
        result = scrape_case_details(case_type, case_number, filing_year)
        log_query(case_type, case_number, filing_year, result['raw_html'])
        return render_template('result.html', result=result)
    except Exception as e:
        return render_template('result.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
