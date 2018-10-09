"""
The purpose of this module is to take the information retrieved from the crawler module (links, CIK, Name)
and output a list of balance sheets, income statements, and cash flow statements.
"""
from crawler import company_name, cik, full_form_links, beautiful_soup_generator
import pandas as pd


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
    balance_sheets = []
    income_statements = []
    cash_flow_statements = []
    for each_df in x:
        if 'total assets' in each_df.index.map(str.lower) and 'total liabilities' in each_df.index.map(str.lower) \
                or 'current assets' in each_df.index.map(str.lower) \
                and 'current liabilities' in each_df.index.map(str.lower) \
                or 'current assets:' in each_df.index.map(str.lower) \
                and 'current liabilities:' in each_df.index.map(str.lower):
            balance_sheets.append(each_df)

    for each_df in x:
        if ('revenues' in each_df.index.map(str.lower) or 'revenue' in each_df.index.map(str.lower)
            or 'revenues:' in each_df.index.map(str.lower) or 'net sales' in each_df.index.map(str.lower)) \
                and ('net income' in each_df.index.map(str.lower) or 'gross profit' in each_df.index.map(str.lower)
                     or 'net loss' in each_df.index.map(str.lower)):
            income_statements.append(each_df)

    for each_df in x:
        if 'cash flows from operating activities' in each_df.index.map(str.lower) \
                or 'cash flows from operating activities:' in each_df.index.map(str.lower) \
                or 'operating activities' in each_df.index.map(str.lower) \
                or 'operating activities:' in each_df.index.map(str.lower):
            cash_flow_statements.append(each_df)

    return balance_sheets, income_statements, cash_flow_statements


"""PROCESS FOR A SINGLE STATEMENT"""

"""# PULL THE FIRST STATEMENT OF THE 10 STATEMENTS FOR CLEANING
bs4_data = beautiful_soup_generator(full_form_links[0])

# CRAWL THE FINANCIAL FILING AND PULL EVERY TABLE
get_every_form_on_the_statement = retrieve_all_tables(bs4_data)
# print(get_that_form)

# GRAB ONLY THE FINANCIAL STATEMENTS I NEED
get_three_financial_statements = retrieve_financial_statements(get_every_form_on_the_statement)
# print(len(get_three_financial_statements))
# print(get_three_financial_statements)
bal, inc, cfw = get_three_financial_statements"""


"""PROCESS fOR MULTIPLE STATEMENTS"""

bal_list = []
inc_list = []
cfw_list = []
for each in full_form_links:
    bs4_data = beautiful_soup_generator(each)
    get_every_form_on_the_statement = retrieve_all_tables(bs4_data)
    get_three_financial_statements = retrieve_financial_statements(get_every_form_on_the_statement)
    bal, inc, cfw = get_three_financial_statements
    bal_list.append(bal)
    inc_list.append(inc)
    cfw_list.append(cfw)
