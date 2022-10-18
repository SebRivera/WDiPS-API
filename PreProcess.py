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
def create_score(row):
    pos_count = row['positive_ratings']
    neg_count = row['negative_ratings']
    total_count = pos_count + neg_count
    average = pos_count / total_count
    return round(average, 2)
def total_ratings(row):
    pos_count = row['positive_ratings']
    neg_count = row['negative_ratings']
    total_count = pos_count + neg_count
    return total_count
df['total_ratings'] = df.apply(total_ratings, axis=1)
df['score'] = df.apply(create_score, axis=1)

# Calculate mean of vote average column
C = df['score'].mean()
# Calculate the minimum number of votes required to be in the chart
m = df['total_ratings'].quantile(0.90)
print(m)

# calculate the weighted rating for each qualified game
# Function that computes the weighted rating of each game
def weighted_rating(x, m=m, C=C):
    v = x['total_ratings']
    R = x['score']
    # Calculation based on the IMDB formula
    return round((v/(v+m) * R) + (m/(m+v) * C), 2)
# Define a new feature 'score' and calculate its value with `weighted_rating()`
df['weighted_score'] = df.apply(weighted_rating, axis=1)
#Print the top 15 games
print(df[['name', 'total_ratings', 'score', 'weighted_score']].head(15))

#We're adding this is for tags with multiple words, we need to connect by '-' before we split them by ' '
df['steamspy_tags'] = df['steamspy_tags'].str.replace(' ','-')
#TF-IDF Vectorizer further down will identify the words by the spaces between the words
df['genres'] = df['steamspy_tags'].str.replace(';',' ')
# count the number of occurences for each genre in the data set
counts = dict()
for i in df.index:
#for each element in list (each row, split by ' ', in genres column)
#-- we're splitting by space so tfidf can interpret the rows
    for g in df.loc[i,'genres'].split(' '):
    #if element is not in counts(dictionary of genres)
        if g not in counts:
            #give genre dictonary entry the value of 1
            counts[g] = 1
        else:
            #increase genre dictionary entry by 1
            counts[g] = counts[g] + 1
#Test Genre Counts
counts.keys()
print(counts['Action'])