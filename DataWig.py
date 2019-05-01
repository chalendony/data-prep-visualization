#!/usr/bin/env python
# coding: utf-8

# # DataWig
# 
# [Exploratory Data Analysis](https://en.wikipedia.org/wiki/Exploratory_data_analysis) (EDA) is an approach to analyzing data sets to summarize and understand their main characteristics, often with visual methods.
# 
# Starting with your *Machine Learning Checklist* you will see that a crucial step is **preparing and understanding** the data. It is a step where you will spend most of your time.  Here is an example checklists from [Aurélien Géron](10_20_2018_Machine-Learning-Project-Checklist.txt) that you can adapt to your needs.   
# 
# In these series of notebooks, we explore the Home Credit data set. We clean, preprocess and visualize the data for downstream processes in the Data Science Workflow.  All notebooks can be obtained from Github : https://github.com/chalendony/data-prep-visualization
# 

# # Python Imports

# In[86]:



import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
    
import pandas as pd
import numpy as np
from pandas.plotting import scatter_matrix
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelBinarizer
pd.set_option('display.max_columns', 125)
import quilt
from scripts.preprocess import percent_missing, align_dataframes, as_dict
from string import Template
import missingno as msno

import impyute
import datawig


# ## Import Quilt Packages from Local Repository 

# In[87]:


from quilt.data.avare import homecredit


# In[88]:


# avoid parens and copy original data
table = 'previous_application'
df = homecredit[table]().copy(deep=True)
df.head()


# In[89]:


# drop keys and empty columns
dropcols = ['RATE_INTEREST_PRIVILEGED','RATE_INTEREST_PRIMARY','SK_ID_PREV', 'SK_ID_CURR']
df.drop(dropcols, axis=1, inplace=True)

# drop rows containing null, also done by datawig?
df.dropna(axis=0, how='any', inplace=True)

# select random instances
seed = 500
numinstances = 1000
df = df.sample(numinstances,random_state=seed)
df.info(verbose=True)


# In[90]:


# assign data types
description = pd.read_excel('data/HomeCredit_columns_description.xlsx', sheet_name='Sheet1',usecols=[2,3,4])
description.head()


# In[91]:


# rename to python types: category , float
python_cat_dtype = 'object'
python_num_dtype = 'float64'

description.replace('categorical', python_cat_dtype, inplace=True)
description.replace('numerical', python_num_dtype, inplace=True)

# type cols
typecols = description[(description.Table == table)]
typecols.head()


# In[93]:


# get target columns 
targetcols = pd.DataFrame(df.columns, columns=['Row'])
targetcols.head()


# In[94]:


# join , ensure col correct -  we dont know which cols are present in the description
targetcols = targetcols.merge(typecols, how='left')
targetcols.head()


# In[98]:


# retrieve all columns of same type 
cat = targetcols.loc[(targetcols.Type == python_cat_dtype),'Row'].values.tolist()
num = targetcols.loc[(targetcols.Type == python_num_dtype),'Row'].values.tolist()

print(cat)
print(num)
#print(len(cat) + len(num))




## batch update types 
df[cat] = df[cat].astype(python_cat_dtype)
df[num] = df[num].astype(python_num_dtype)
df.info()


# In[97]:



# select a portion of the data for evaluation
df_train, df_test = datawig.utils.random_split(df)




output_column = 'PRODUCT_COMBINATION'
output_path = 'imputer_model'
lst = [*df.columns.values]
lst.remove(output_column)
input_cols = lst



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


