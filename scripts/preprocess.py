import  pandas as pd

#todo code is wrong COMMONAREA_MEDI is not categorical
def percent_missing(df, cols):
    total = df.isnull().sum().sort_values(ascending=False)
    percent = (df.isnull().sum() / df.isnull().count() * 100).sort_values(ascending=False)
    missing_application_train_data = pd.concat([total, percent], axis=1, keys=['Total', 'Perc_Missing'])
    return missing_application_train_data.loc[cols].sort_values(ascending=False, by='Perc_Missing')
