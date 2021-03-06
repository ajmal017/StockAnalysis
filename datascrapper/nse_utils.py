from datascrapper import nse_urls
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def findNextExpiryDatesForStocks():
    future_date_format = '%d%b%Y'
    nse_fno_data = nse_urls.get_nifty_fno_url().text
    match = re.findall(r'\d\d(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\d{4}', nse_fno_data)
    expiry_dates_list = list(dict.fromkeys(match))
    expiry_dates = [datetime.strptime(expiry_date, future_date_format) for expiry_date in expiry_dates_list]
    return expiry_dates


def findNextExpiryDatesForIndices():
    future_date_format = '%d%b%Y'
    nse_indices_opt_chain = nse_urls.get_nifty_opt_chain_url().text
    soup = BeautifulSoup(nse_indices_opt_chain, 'html.parser')
    result = soup.find(id='date')
    option = result.select('option[value]')
    expiry_dates_list = [item.get('value') for item in option if item.get('value') != 'select']
    expiry_dates = [datetime.strptime(expiry_date, future_date_format) for expiry_date in expiry_dates_list]
    #print(expiry_dates)
    return expiry_dates


def getLastUpdateOptionDate():
    nse_option_home_url = nse_urls.get_option_chain_updated_date_url().text
    print(nse_option_home_url)
    match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{2},\s\d{4}', nse_option_home_url)
    print(match.group(0))
    last_updated_date = datetime.strptime(match.group(0),'%b %d, %Y').date()
    return last_updated_date
