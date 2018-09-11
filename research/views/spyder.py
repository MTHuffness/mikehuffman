import requests
from bs4 import BeautifulSoup as soup
import pandas as pd
from datetime import timedelta
import time
import re
from tabulate import tabulate

pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 30)
pd.set_option('display.width', 1000)

expire_after = timedelta(days=1)
#requests_cache.install_cache('nobel_pages', backend='sqlite', expire_after=expire_after)

symbol = 'nvda'
form = '10-Q'
financial_report = 'Consolidated Balance Sheets (Unaudited)'
base_url = 'https://www.sec.gov'
url = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK={}&owner=exclude&action=getcompany&Find=Search'.format(symbol)


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


edgar_search_page = beautiful_soup_generator(url)


def get_company_cik(x):
    """
    A function that grabs the CIK for a company based on the Symbol derived URL.

    :param x: The bsoup object returned from company search().
    :return: the string format of the CIK for the company.
    """

    full_cik = x.find('div', {'class': 'companyInfo'}).find('a').text
    cik = [x for x in full_cik.split() if x.isdigit()]
    return cik[0]


cik = get_company_cik(edgar_search_page)
edgar_company_filing_page = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&' \
       'CIK={cik}&' \
       'type={form}&dateb=&owner=exclude&count=10'.format(cik=cik, form=form)
bs4 = beautiful_soup_generator(edgar_company_filing_page)


def get_company_content(x):
    """A Function that takes in the URL and returns the Company Info from the filing search page."""
    content = x.find('div', {'class': 'companyInfo'})
    return content


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


broad_form_links = get_company_documents_page_links(bs4)


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


def retrieve_all_tables(x):
    """
    This function takes the actual financial report and creates a database for every table,
    whether or not the the table represents a financial statement of interest. the function
    then scans each table to determine if it is one of the 3 statements of interest.
    :param x:
    :return:
    """
    list_of_dataframes = []
    for item in x.findAll('table'):
        data_list = []
        for tr in item.findAll('tr'):
            tds = tr.findAll('td')
            row = [tr.text.strip() for tr in tds]
            data_list.append(row)
        data_frame = pd.DataFrame(data_list)
        data_frame = data_frame.set_index(data_frame[0])
        list_of_dataframes.append(data_frame)
    return list_of_dataframes


def retrieve_financial_statements(x):
    """
    this function looks through the entire list of databases from retrieve_all_tables() and
    searches for the statements that contain the contents within a financial statement and
    returns a list of these statements. the goal is to scale the function to return the 3
    primary financial statements for any symbol selected.
    :param x: the list of databases from the retrieve_all_tables() function
    :return: a list of databases that contain only the 3 primary financial statements.
    """
    financial_reports = []
    for each_df in x:
        if 'total assets' in each_df.index.map(str.lower) and 'total liabilities' in each_df.index.map(str.lower) \
                or 'current assets' in each_df.index.map(str.lower) \
                and 'current liabilities' in each_df.index.map(str.lower):
            financial_reports.append(each_df)

    for each_df in x:
        if ('revenues' in each_df.index.map(str.lower)
            or 'revenues:' in each_df.index.map(str.lower) or 'net sales' in each_df.index.map(str.lower)) \
                and 'net income' in each_df.index.map(str.lower):
            financial_reports.append(each_df)

    for each_df in x:
        if 'cash flows from operating activities' in each_df.index.map(str.lower) \
                or 'cash flows from operating activities:' in each_df.index.map(str.lower) \
                or 'operating activities' in each_df.index.map(str.lower) \
                or 'operating activities:' in each_df.index.map(str.lower):
            financial_reports.append(each_df)

    return financial_reports


full_form_links = [get_company_financial_link(beautiful_soup_generator(x)) for x in broad_form_links]
print(full_form_links)

bs4_data = beautiful_soup_generator(full_form_links[0])
get_every_form_on_the_statement = retrieve_all_tables(bs4_data)
# print(get_that_form)

get_three_financial_statements = retrieve_financial_statements(get_every_form_on_the_statement)
print(len(get_three_financial_statements))
print(get_three_financial_statements)