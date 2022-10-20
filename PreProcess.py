import pandas as pd
import numpy as np
import re
import itertools
## import matplotlib.pyplot as plt
def importData(filename):
    df = pd.read_csv(filename, encoding = "utf-8")
    ##fileName = "Data\steam.csv"
    return df

#These are just quick checks to make sure the dataset looks correct
## print(df.shape)
## df.head()

#Which columns have null values?
##print(df.columns[df.isna().any()].tolist())
#How many null values per column? - Count the missing values in each column
##df.isnull().sum()

# Extracts the year from the release date
def extractYear(date):
    year = date[:4]
    if year.isnumeric():
        return int(year)
    else:
        return np.nan

def totalRatings(row):
    posCount = row['positive_ratings']
    negCount = row['negative_ratings']
    totalCount = posCount + negCount
    return totalCount
def createScore(row):
    posCount = row['positive_ratings']
    negCount = row['negative_ratings']
    totalCount = posCount + negCount
    average = posCount / totalCount
    return round(average, 2)

def addScoreAndTotalRatings(df):
    df['score'] = df.apply(createScore, axis=1)
    df['total_ratings'] = df.apply(totalRatings, axis=1)
    return df


# calculate the weighted rating for each qualified game
# Function that computes the weighted rating of each game
def weighted_rating(x, m, C):
    v = x['total_ratings']
    R = x['score']
    # Calculation based on the IMDB formula
    return round((v/(v+m) * R) + (m/(m+v) * C), 2)

def addWeightedRating(df):
    # Calculate mean of vote average column
    C = df['score'].mean()
    # Calculate the minimum number of votes required to be in the chart
    m = df['total_ratings'].quantile(0.90)
    # Define a new feature 'score' and calculate its value with `weighted_rating()`
    df['weighted_score'] = df.apply(weighted_rating, axis=1, args=(m, C))
    return df

def combine(x, colA, colB):
    return x[colA] + ' ' + x[colB]

def formatColumns(df):
    #We're adding this is for tags with multiple words, we need to connect by '-' before we split them by ' '
    df['steamspy_tags'] = df['steamspy_tags'].str.replace(' ','-')
    #TF-IDF Vectorizer further down will identify the words by the spaces between the words
    df['genres'] = df['steamspy_tags'].str.replace(';',' ')
    
    df['categories'] = df['categories'].str.replace(' ','-')
    df['categories'] = df['categories'].str.replace(';',' ')
    features = ('steamspy_tags','categories')
    df['merged'] = df.apply(combine, axis=1, args = features)
    
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
    return df