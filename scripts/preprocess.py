import pandas as pd


def percent_missing(df, cols):
    """
    count() : Count non-NA cells for each column or row. The isnull method returns a DataFrame of all boolean values (True/False).
    and the shape of the DataFrame does not change from the original - so we are counting all row present in the dataframe
    Cool one-liner to compute percent missing: df.isna().mean().round(4) * 100
    :param df:
    :param cols: filter rows
    :return:
    """
    total = df.isnull().sum().sort_values(ascending=False)
    percent = (df.isnull().sum() / df.isnull().count() * 100).sort_values(ascending=False)
    missing_application_train_data = pd.concat([total, percent], axis=1, keys=['Total', 'Perc_Missing'])
    return missing_application_train_data.loc[cols].sort_values(ascending=False, by='Perc_Missing')




def as_dict(df):

    # white space
    df['Row'] = df['Row'].str.strip()
    df['Type'] = df['Type'].str.strip()

    # rename types
    df.replace('numerical', 'float64', inplace=True)
    df.replace('categorical', 'category', inplace=True)

    # convert to dict
    tuples = dict([*zip(df.Row.values, df.Type.values)])
    return tuples

