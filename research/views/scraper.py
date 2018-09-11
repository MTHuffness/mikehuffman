from .spyder import get_every_form_on_the_statement


def retrieve_financial_statements(x):
    """

    :param x:
    :return:
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


get_three_financial_statements = retrieve_financial_statements(get_every_form_on_the_statement)
print(len(get_three_financial_statements))
print(get_three_financial_statements)
