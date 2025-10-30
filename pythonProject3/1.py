import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
df = pd.read_csv('data-week-3.csv')

df.columns = df.columns.str.lower().str.replace(' ', '_')

categorical_columns = list(df.dtypes[df.dtypes == 'object'].index)

for c in categorical_columns:
    df[c] = df[c].str.lower().str.replace(' ', '_')

df.totalcharges = pd.to_numeric(df.totalcharges, errors='coerce')
df.totalcharges = df.totalcharges.fillna(0)

df.churn = (df.churn == 'yes').astype(int)
df_full_train, df_test = train_test_split(df, test_size=0.2, random_state=1)
categorical = ['lead_source']
numeric = ['number_of_courses_viewed', 'annual_income']

df[categorical] = df[categorical].fillna('NA')
df[numeric] = df[numeric].fillna(0)

train_dict = df[categorical + numeric].to_dict(orient='records')

pipeline = make_pipeline(
    DictVectorizer(),
    LogisticRegression(solver='liblinear')
)

pipeline.fit(train_dict, y_train)