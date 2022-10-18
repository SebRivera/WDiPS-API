import pandas as pd
import numpy as np
import re
import itertools
# import matplotlib.pyplot as plt

fileName = "Data\steam.csv"
df = pd.read_csv(fileName,  error_bad_lines=False, encoding='utf-8')
#These are just quick checks to make sure the dataset looks correct
print(df.shape)
df.head()

#Which columns have null values?
print(df.columns[df.isna().any()].tolist())
#How many null values per column? - Count the missing values in each column
df.isnull().sum()
print("TEst")

# Extracts the year from the release date
def extract_year(date):
    year = date[:4]
    if year.isnumeric():
        return int(year)
    else:
        return np.nan
df['year'] = df['release_date'].apply(extract_year)

#Create score column
def totalRatings(row):
    posCount = row['positive_ratings']
    negCount = row['negative_ratings']
    totalCount = posCount + negCount
    return posCount, negCount, totalCount
def createScore(row):
    posCount, negCount, totalCount = totalRatings(row)
    average = posCount / totalCount
    return round(average, 2)
df['total_ratings'] = df.apply(totalRatings[2], axis=1)
df['score'] = df.apply(createScore, axis=1)