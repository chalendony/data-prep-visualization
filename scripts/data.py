import pandas as pd


categorical_features = ['TARGET','SK_ID_CURR','WALLSMATERIAL_MODE','EMERGENCYSTATE_MODE','FONDKAPREMONT_MODE','HOUSETYPE_MODE', 'NAME_CONTRACT_TYPE','CODE_GENDER','FLAG_OWN_CAR','FLAG_OWN_REALTY','NAME_TYPE_SUITE', \
                        'NAME_INCOME_TYPE','NAME_EDUCATION_TYPE','NAME_FAMILY_STATUS','NAME_HOUSING_TYPE','FLAG_MOBIL','FLAG_EMP_PHONE',\
                        'FLAG_WORK_PHONE','FLAG_CONT_MOBILE','FLAG_PHONE','FLAG_EMAIL','OCCUPATION_TYPE',\
                        'REGION_RATING_CLIENT','REGION_RATING_CLIENT_W_CITY','WEEKDAY_APPR_PROCESS_START','HOUR_APPR_PROCESS_START',\
                        'REG_REGION_NOT_LIVE_REGION','REG_REGION_NOT_WORK_REGION','LIVE_REGION_NOT_WORK_REGION','REG_CITY_NOT_LIVE_CITY',\
                        'REG_CITY_NOT_WORK_CITY','LIVE_CITY_NOT_WORK_CITY','ORGANIZATION_TYPE','FLAG_DOCUMENT_2','FLAG_DOCUMENT_3',\
                        'FLAG_DOCUMENT_4','FLAG_DOCUMENT_5','FLAG_DOCUMENT_6','FLAG_DOCUMENT_7','FLAG_DOCUMENT_8','FLAG_DOCUMENT_9',\
                        'FLAG_DOCUMENT_10','FLAG_DOCUMENT_11','FLAG_DOCUMENT_12','FLAG_DOCUMENT_13','FLAG_DOCUMENT_14','FLAG_DOCUMENT_15',\
                        'FLAG_DOCUMENT_16','FLAG_DOCUMENT_17','FLAG_DOCUMENT_18','FLAG_DOCUMENT_19','FLAG_DOCUMENT_20','FLAG_DOCUMENT_21']

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