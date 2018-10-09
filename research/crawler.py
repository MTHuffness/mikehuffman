"""
The purpose of this module is to crawl the SEC website and deliver the filing links, the company name,
and the company CIK.
"""
import requests
from bs4 import BeautifulSoup as soup
import numpy as np
import pandas as pd
from datetime import timedelta
import time
import re
from collections import defaultdict
from functools import reduce
from datetime import datetime

pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)


def beautiful_soup_generator(x):
    """This function works the BeautifulSoup for you for easy access. This function will take
    you to the EDGAR search results page with all the filings for the symbol.
    :param x: The url received from url. This url takes you to the generalized search page.
    Returns:
        The BeautifulSoup object.
    """

    response = requests.get(x)
    # bsoup = soup(response.content, 'html.parser')
    bsoup = soup(response.content, 'lxml')
    return bsoup


"""def get_company_cik(x):

    A function that grabs the CIK for a company based on the Symbol derived URL.

    :param x: The bsoup object returned from company search().
    :return: the string format of the CIK for the company.


    full_cik = x.find('div', {'class': 'companyInfo'}).find('a').text
    cik = [x for x in full_cik.split() if x.isdigit()]
    return cik[0]"""


def get_company_content(x):
    """A Function that takes in the URL and returns the Company Info from the filing search page."""
    content = x.find('div', {'class': 'companyInfo'})
    full_company_name = content.find('span', {'class': 'companyName'}).text
    company_info = full_company_name.split()
    cik = company_info[3]
    company_name = company_info[0] + " " + company_info[1]
    # cik_link = content.find('a').text
    # cik = [x for x in cik_link.split() if x.isdigit()]
    return company_name, cik


def get_company_documents_page_links(x):
    """
    This function takes the bs4 for the specific symbol/form search page and locates the
    links for the documents page. This crawls the site that has the form/symbol of search
    in order to create a full list of links to each documents page.

    :param x: the bs4 for the specified symbol/form search page.
    :return: A list of all the links to the documents SEC filing site for the symbol.
    """
    sec_table = x.find(name='table', attrs={'class': 'tableFile2'})
    link_list = [base_url + item.find('a', {'id': 'documentsbutton'}).attrs['href']
                 for item in sec_table.findAll('tr')[1:]]
    return link_list


def get_company_financial_link(x):
    """This function takes the link from get_company_documents_page_links() and
    returns the link for the actual form for the filing. This is the endpoint in
    terms of crawling to where the forms are.
    Argument:
        x: The URL from the get_company_interactive_page_links() function.
    Returns:
        The link to the actual form content.
    """

    form_table = x.find('table', {'class': 'tableFile'})
    outer_form_link = form_table.findAll('tr')[1]
    inner_form_link = outer_form_link.find('a').attrs['href']
    return base_url + inner_form_link

# variables


symbol = 'aapl'
form = '10-q'
base_url = 'https://www.sec.gov'
url = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK={}&owner=exclude&action=getcompany&Find=Search'.format(symbol)

edgar_search_page = beautiful_soup_generator(url)
company_name, cik = get_company_content(edgar_search_page)
edgar_company_filing_page = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&' \
                            'CIK={cik}&' \
                            'type={form}&dateb=&owner=exclude&count=10'.format(cik=cik, form=form)
bs4 = beautiful_soup_generator(edgar_company_filing_page)
company_information = get_company_content(edgar_search_page)
# print(company_name, ",", cik)
broad_form_links = get_company_documents_page_links(bs4)
full_form_links = [get_company_financial_link(beautiful_soup_generator(x))
                   for x in broad_form_links]
# print(full_form_links)
