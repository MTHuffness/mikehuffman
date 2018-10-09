"""
The purpose of this module is to take the information retrieved the unclean balance sheet list
 from the statement_search module and clean each list separately. Once each balance sheet has
 cleaned, they can then all be combined together to form a data frame with the balance sheet
 data from the previous 10 filings.
"""
from statement_search import bal, bal_list
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
import string


def clean_and_merge(x):
    location = []
    date = []
    year = []
    full_date = []
    year_pattern = re.compile('2[0-9][0-9][0-9]')

    x.replace('', np.nan, inplace=True)  # replace all empty strings with NaN for row/column removal
    x = x.dropna(axis=1, how='all')
    x = x.dropna(axis=0, how='all')
    x = x.fillna('')  # replace all the NaN back to a empty string for concatenation
    x = x.drop(x.iloc[:, [0]], axis=1)  # drop the duplicate column that was moved to be an index

    # searches for the month in each column of the top row, if it is there, add the month
    # name and its location for column naming and column combining purposes.
    for key, column in enumerate(x.iloc[0, :]):
        if column:
            date.append(column)
            location.append(key)
    location.append(len(x.iloc[0, :]))

    # ISSUE
    """depending on whether or not the year is added into the top row, a different 
    method is required to create the column title:
        year in:
            fun_db needs columns to be date and fin_dict draws from date
        year not in:
            replace date in the above spots with full_date"""

    x.replace(np.nan, '', inplace=True)  # replace all empty strings with NaN for row/column removal

    for key, yr in enumerate(x.iloc[1]):
        if yr and bool(year_pattern.match(yr)):
            year.append(yr)

    for lis in range(len(date)):
        full_date.append(date[lis] + ' ' + year[lis])

    # NOTE
    """looks like i need to match the index of the list date with the index of
    the location. I could essentially remove the rows with the dates completely
    and then create a new row where column 0 is date 0 all the way up... easy!!"""

    """this function take the location data and creates a dictionary out of it for 
    purposes of combining the columns together."""
    indexer = defaultdict(list)
    for index, item in enumerate(location):
        if item != location[-1]:
            end_point = location[index + 1]
            while item < end_point:
                indexer[index].append(item)
                item += 1
        else:
            break

    fin_dict = {full_date[key]: x.iloc[:, lis[:]].sum(axis=1)
                for key, lis in indexer.items()}
    fin_db = pd.DataFrame(fin_dict, columns=full_date)
    # fin_db = pd.DataFrame(fin_dict)
    fin_db = fin_db.drop(fin_db.index[0])

    return fin_db, date


"""PROCESS FOR A SINGLE STATEMENT"""

# CLEAN THE STATEMENT
cbal, c_month = clean_and_merge(bal_list[0][0])
print(cbal)

"""PROCESS fOR MULTIPLE STATEMENTS"""


cbal_list = []
for item in bal_list:
    cbal = clean_and_merge(item[0])
    # print(cbal[0].index)  # checks the info for each statement and determine the number of rows
    # print(cbal[0])
    cbal_list.append(cbal[0])

"""
# merge all the data frames together into a single data frame
bst = pd.concat(cbal_list, axis=1, sort=False)
# remove all the duplicate columns
bst = bst.loc[:, ~bst.columns.duplicated()]
# bst.columns.astype('datetime64')
print(bst)"""
