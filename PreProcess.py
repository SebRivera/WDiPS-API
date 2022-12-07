import pandas as pd
import numpy as np
import re

#Function to import the data from the csv file
def importData(filename):
    #fileName = "Data\steam.csv"
    df = pd.read_csv(filename, encoding = "utf-8")
    return df

#Function to drop rows with no playtime
def dropNoPlayRimeRows(df):
    idxNoPTR = df[(df['average_playtime'] == 0)].index
    df.drop(idxNoPTR , inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

#Function to drop rows with no name or no developer, and no publisher
def dropNoNameDevPub(df):
    idxNoNDP = df[(df['name'] == '')].index
    df.drop(idxNoNDP , inplace=True)
    df.reset_index(drop=True, inplace=True)
    idxNoNDP = df[(df['developer'] == '') & (df['publisher'] == '')].index
    df.drop(idxNoNDP , inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# Extracts the year from the release date
def extractYear(date):
    year = date[:4]
    if year.isnumeric():
        return int(year)
    else:
        return np.nan

#Function to get the total amount of ratings
def totalRatings(row):
    posCount = row['positive_ratings']
    negCount = row['negative_ratings']
    totalCount = posCount + negCount
    return totalCount
#Function to create the average Score of the ratings
def createScore(row):
    posCount = row['positive_ratings']
    negCount = row['negative_ratings']
    totalCount = posCount + negCount
    average = posCount / totalCount
    return round(average, 2)
#Function to add the score and total ratings to the dataframe
def addScoreAndTotalRatings(df):
    df['score'] = df.apply(createScore, axis=1)
    df['total_ratings'] = df.apply(totalRatings, axis=1)
    return df
    
def replace_foreign_characters(s):
    return re.sub(r'[^\x00-\x7f]',r'', s)

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

def combine(x, *features):
    result = ''
    for f in features:
        result += str(x[f]) + ' '
    return result

def updateAvgPlaytime(df):
    if df['average_playtime'] > 0 and df['average_playtime'] < 200:
        return 'VeryLow-PT'
    elif df['average_playtime'] >= 200 and df['average_playtime'] < 400:
        return 'Low-PT'
    elif df['average_playtime'] >= 400 and df['average_playtime'] < 700:
        return 'Med-PT'
    elif df['average_playtime'] >= 700 and df['average_playtime'] < 1000:
        return 'High-PT'
    elif df['average_playtime'] >= 1000 and df['average_playtime'] < 4999:
        return 'VeryHigh-PT'
    elif df['average_playtime'] >= 5000:
        return 'Extreme-PT'

# Function which contains all processes of formating.
def formatColumns(df):
    #Clean up all foreign characters and non ASCII characters
    df.astype(str).apply(lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))
    df['name'] = df['name'].apply(lambda x: replace_foreign_characters(x))
    df['developer'] = df['developer'].apply(lambda x: replace_foreign_characters(x))
    df['publisher'] = df['publisher'].apply(lambda x: replace_foreign_characters(x))
    #We clean up some extra characters
    df['name'] = df['name'].str.replace('™','')
    df['name'] = df['name'].str.replace('®','')
    df['name'] = df['name'].str.replace('’','')
    df['developer'] = df['developer'].str.replace('™','')
    df['publisher'] = df['publisher'].str.replace('™','')
    #We clean up some extra spaces
    df['name'] = df['name'].str.strip()
    df['developer'] = df['developer'].str.strip()
    df['publisher'] = df['publisher'].str.strip()
    #Since some tags have multiple words, we need to connect them with '-', before we split them with ' '
    df['steamspy_tags'] = df['steamspy_tags'].str.replace(' ','-')
    df['categories'] = df['categories'].str.replace(' ','-')
    #TF-IDF Vectorizer further down will identify the words by the spaces between the words
    df['genres'] = df['steamspy_tags'].str.replace(';',' ')
    df['categories'] = df['categories'].str.replace(';',' ')

    #We replace average playtime with a categorical value
    df['average_playtime'] = df.apply(updateAvgPlaytime, axis=1)
    #List of features to combine
    features = ['steamspy_tags','categories', 'average_playtime', 'required_age']
    #Compine the features into one column
    df['merged'] = df.apply(combine, axis=1, args = features)
    return df