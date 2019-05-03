import pandas as pd
from quilt.data.avare import homecredit

def create_new_data_description():
    #### why cant i  persistance my data types!!!
    # 1) rename types in data description to python types,
    # 2) override panda-inferred types
    # 3) fix error: create a new description file - mis-match between data columns in data and metadata files.
    # 4) prevent repeating this step for each each execution of the code - create new file once and load it when needed
    # 5) document lessons learned: using type category made lots of headache because the api was attempting to insert into the category.
    # using objects to represent categorical instead of category resolved the problem!
    #### Check, may not need to convert to feature tool types - not sure if since the types are inferred.

    # read old  metadata file , white space in the some colums ...bump...removed manually
    description = pd.read_excel('data/HomeCredit_columns_description.xlsx', sheet_name='Sheet1', usecols=[2, 3, 4])

    new_cat_dtype = 'object'
    new_num_dtype = 'float64'
    old_cat_dtype = 'categorical'
    old_num_dtype = 'numerical'

    description.replace(old_cat_dtype, new_cat_dtype, inplace=True)
    description.replace(old_num_dtype, new_num_dtype, inplace=True)

    appended_data = []

    for key, val in homecredit._items():
        df = val()
        print(key)

        # select types for the target cols
        types = description[(description.Table == key)]

        # select the target columns
        targetcols = pd.DataFrame(df.columns, columns=['Row'])

        # perform join:
        targetcols = targetcols.merge(types, how='left')
        appended_data.append(targetcols)

    pd.concat(appended_data).to_csv('data/new_data_description_file.csv', index=False)


htsensor_columns = ['timestamp', 'Start Symbol', 'Zustand', 'Zeitstempel', 'Temp1', 'Temp2', 'Temp3', 'Temp4', 'Temp5',
                    'Temp6', 'Temp7', 'Temp8', 'Humi1', 'Humi2', 'Humi3', 'Humi4', 'Humi5', 'Humi6', 'Humi7', 'Humi8',
                    'Temperatur Kombisensor', 'Humid Kombisensor', 'Windgeschwindigkeit', 'Niederschlag', 'Rain',
                    'Stop Symbol'
                    ]



def braunschweig(url):

    # read data from file: parse the date after reading, just as a sanity check
    df = pd.read_csv(url, sep=';', decimal=',', names=htsensor_columns)

    # select relevant columns
    df = df[['timestamp', 'Temp1', 'Temp2', 'Temp3', 'Temp4', 'Temp8', 'Humi1', 'Humi2', 'Humi3', 'Humi4']]

    # create time series by parsing timestamp, and insert it as new column
    df.insert(1, 'datetime',
                pd.to_datetime(df.timestamp, errors='coerce'))  # If ‘coerce’, then invalid parsing will be set as NaT

    # set the date as the index
    df.set_index('datetime', inplace=True)

    # remove the orginal time
    df.drop(columns='timestamp', inplace=True)

    return df


def deutsches_wetterdienst(url, start=2014, end=2017):

    df = pd.read_csv(url, sep=';')

    # parse date
    df.insert(2, 'datetime', pd.to_datetime(df['MESS_DATUM'], errors='coerce', format='%Y%m%d%H'))

    # create index
    df.set_index('datetime', inplace=True)

    # rename columns
    df.rename(columns={'TT_TU': 'Temp', 'RF_TU': 'Humi'}, inplace=True)

    # filter years
    span = (df.index.year >= start) & (df.index.year <= end)
    df = df.loc[span, ['Temp', 'Humi']]

    # drop erroneous data points
    dropidx = df[df.Humi < 0].index
    df.drop(dropidx, inplace=True)
    
    return df