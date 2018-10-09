from django.shortcuts import render
# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import quandl as q
import random
import time
from pprint import pprint as pp

# pd.set_option('display.max_columns', 30)
# pd.set_option('display.max_rows', 30)
# pd.set_option('display.width', 1000)

q.ApiConfig.api_key = 'CfZbDf_qynZ238VAa9Wd'

"""
    PULL THE APPLE DATA AND CLEAN IT BY REPLACING 'NONE' WITH NAN AND THEN 
    REMOVING ALL THE ROWS WITH NAN. FINALLY CREATE A NEW DATABASE CONSISTING 
    OF THE MOST RECENT 50 FILINGS.
"""
aapl = pd.read_csv('../static/csv_files/AAPL_quarterly_financial_data.csv',
                   index_col='Quarter end', parse_dates=True)
aapl.replace('None', np.nan, inplace=True)
aapl = aapl.dropna(axis=0)
aapl = aapl.astype('float64')
aapl = aapl.head(50)

"""slice only for the QTR ending in June"""
aapl_qt2 = aapl.loc[(aapl.index.month == 6) | (aapl.index.month == 7)]

