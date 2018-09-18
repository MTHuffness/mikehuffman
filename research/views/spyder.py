import requests
from bs4 import BeautifulSoup as soup
import numpy as np
import pandas as pd
from datetime import timedelta
import time
import re
from collections import defaultdict

pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)


symbol = 'aapl'
form = '10-q'
base_url = 'https://www.sec.gov'
url = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK={}&owner=exclude&action=getcompany&Find=Search'.format(symbol)
location = []
month_list = []


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
        data_frame = data_frame.set_index(data_frame.loc[:, 0])
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
                and 'current liabilities' in each_df.index.map(str.lower)\
                or 'current assets:' in each_df.index.map(str.lower) \
                and 'current liabilities:' in each_df.index.map(str.lower):
            financial_reports.append(each_df)

    for each_df in x:
        if ('revenues' in each_df.index.map(str.lower) or 'revenue' in each_df.index.map(str.lower)
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


def clean_financial_data(x):
    """
    This function looks to remove any unnecessary blemishes from the financial document. First
    it cleans and rows or columns with no data, then drops any repetitive columns. The function
    also searches for where the months are in the statement and works to build a list of the
    referenced months in the statement & where they are located.
    :param x: The uncleaned financial statement returned from retrieve_financial_statements()
    :return: a cleaned version of the statement.
    """
    # clean the data
    x.replace('', np.nan, inplace=True)  # replace all empty strings with NaN for row/column removal
    x = x.dropna(axis=1, how='all')
    x = x.dropna(axis=0, how='all')
    x = x.fillna('')  # replace all the NaN back to a empty string for concatenation
    x = x.drop(x.iloc[:, [0]], axis=1)  # drop the duplicate column that was moved to be an index
    month = ['January', 'February', 'March', 'April', 'May', 'June',
             'July', 'August', 'September', 'October', 'November', 'December']
    # pull the row and column for the values that contain months. this is to have the dataframe
    # automatically use this location to combine columns together under the appropriate month.
    for number in range(len(x.iloc[0, :])):
        for z in month:
            for item in x.iloc[:, number].str.contains(z):
                if item:
                    month_list.append(z)
                    location.append(number)
    location.append(len(x.iloc[0, :]))

    return x


def create_column_dict(x):
    """
    This function is built to determine how many months are contained in the financial data
    and to split the filing so that the columns combined are for the appropriately referened
    month.
    :return: a dictionary of lists. each dict key is the index for the month and the values
    are the columns of data that need to be combined for that index. Also returns the list
    of columns which will be needed when you remove them after the columns are combined.
    """
    indexer = defaultdict(list)
    for index, item in enumerate(location):
        if item != location[-1]:
            end_point = location[index + 1]
            while item < end_point:
                indexer[index].append(item)
                item += 1
        else:
            break
    return indexer, location


def merge_columns_together(pack, x):
    """

    :param x:
    :return:
    """
    fin_dict = {month_list[key]: x.iloc[:, lis[:]].sum(axis=1) for key, lis in pack[0].items()}
    fin_db = pd.DataFrame(fin_dict)
    return fin_db


"""PROCESS"""

# CRAWL FOR THE LINKS OF THE 10 MOST RECENT STATEMENTS
full_form_links = [get_company_financial_link(beautiful_soup_generator(x)) for x in broad_form_links]
#print(full_form_links)

# PULL THE FIRST STATEMENT OF THE 10 STATEMENTS FOR CLEANING
bs4_data = beautiful_soup_generator(full_form_links[0])

# CRAWL THE FINANCIAL FILING AND PULL EVERY TABLE
get_every_form_on_the_statement = retrieve_all_tables(bs4_data)
# print(get_that_form)

# GRAB ONLY THE FINANCIAL STATEMENTS I NEED
get_three_financial_statements = retrieve_financial_statements(get_every_form_on_the_statement)
# print(len(get_three_financial_statements))
# print(get_three_financial_statements)
bs = get_three_financial_statements

# CLEAN THE STATEMENT
cs = clean_financial_data(bs[0])

# LIST FORMAT FOR THE COLUMNS AND MONTHS
# print(location)
# print(month_list)

# CREATE A DICTIONARY WITH THE KEYS BEING THE NUMBER OF COLUMNS NEEDED AND THE VALUES BEING
# HOW MANY COLUMNS NEED TO BE CONDENSED INTO IT
column_pack = create_column_dict(cs)
# print(column_pack)

# FINAL CLEAN - MERGE COLUMNS TOGETHER INTO A NEW DATABASE
final = merge_columns_together(column_pack, cs)
print(final)
