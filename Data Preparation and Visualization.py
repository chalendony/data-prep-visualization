
import pandas as pd
import numpy as np
import quilt
from scripts.preprocess import percent_missing, align_dataframes, as_dict
import datawig
from quilt.data.avare import homecredit


quilt.ls()

# avoid parens and copy original data
frames = {}
for key, val in homecredit._items():
    frames[key] = val().copy(deep=True)


# ## Set Data Types
# 
# * Pandas.read_csv() infers the data types. Sometimes the types are not as we would like.
# * Load the data description file, containing the data types

# ### Load Data Description File
# 		
# * A copy of the data desciption file can be found here: [Data Description](data/HomeCredit_columns_description.txt)
# * Avoid opening the .xlsx version to prohibit unintensional modification; it is loaded as a dataframe.

# In[5]:


hc_description = pd.read_excel('data/HomeCredit_columns_description.xlsx', sheet_name='Sheet1',usecols=[2,3,4])
hc_description.head()


# ### Fix Error is Data Description
# 
# * Some error in the data: A column in the description file is not present in the data file

idx = hc_description[(hc_description.Row == 'NFLAG_MICRO_CASH') & (hc_description.Table == 'previous_application')].index
hc_description.drop(idx, inplace=True)


# ### Update Data Types 
# 
# * Pandas read columns as objects, we convert them to category and fix any mis-typed columns manually.


for table in frames.keys():
    print(table)  
    
    # retriev type from description
    df = hc_description.loc[hc_description['Table']==table,['Row','Type']]
    dict_types = as_dict(df)
    
    # set types in data table
    frames[table] = frames[table].astype(dict_types)


frames = align_dataframes(frames)

# # Missing Data Strategy
# 

# create subset ...
table = 'previous_application'
seed = 300
numinstances = 1000
datatype = 'category'
df = frames[table].copy(deep=True)

# drop empty - I think this is done in the datawig 
#df.dropna(axis=0, how='any', inplace=True)

# select random instances
df = df.sample(numinstances,random_state=seed)

# remove numeric columns
df = df.select_dtypes(include=['category'])

# error in manual process
df.drop(['HOUR_APPR_PROCESS_START','NFLAG_LAST_APPL_IN_DAY','SELLERPLACE_AREA','NFLAG_INSURED_ON_APPROVAL'], axis=1, inplace=True)

df.head()


# In[148]:


df.shape


# In[149]:


## distinct values 
df.PRODUCT_COMBINATION.nunique()


# In[157]:


# overall: counts for each value
df.PRODUCT_COMBINATION.value_counts()


# In[151]:


# select a portion of the data for evaluation
df_train, df_test = datawig.utils.random_split(df)
print(df_test.shape)
print(df_train.shape)


# In[152]:


df.info()


# In[153]:



input_cols = [*df.columns.difference(['SK_ID_PREV', 'SK_ID_CURR']).values]
output_column = 'PRODUCT_COMBINATION'
output_path = 'imputer_model'

# Initialize a SimpleImputer model
imputer = datawig.SimpleImputer(
    input_columns=input_cols,  # columns containing information about the column we want to impute
    output_column='PRODUCT_COMBINATION',  # the column we'd like to impute values for
    output_path=output_path  # stores model data and metrics
)

# Fit an imputer model on the train data
#imputer.fit(train_df=df_train, num_epochs=5)

# Fit an imputer model with default list of hyperparameters
imputer.fit_hpo(train_df=df_train)

# Impute missing values and return original dataframe with predictions
predictions = imputer.predict(df_test)

# Calculate f1 score for true vs predicted values
f1 = datawig.f1_score(predictions[output_column], predictions[output_column+'_imputed'], average='weighted')

# Print overall classification report
print(datawig.classification_report(predictions[output_column], predictions[output_column+'_imputed']))



