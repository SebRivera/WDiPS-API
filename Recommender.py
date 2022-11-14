import PreProcess
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from fuzzywuzzy import fuzz
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="wdips-functions\wdips-creds.json"



def matching_score(a,b):
   return fuzz.ratio(a,b)
   # exactly the same, the score becomes 100

def get_appid_from_index(df, index):
   return df[df.index == index]['appid'].values[0]
def get_title_year_from_index(df, index):
   return df[df.index == index]['year'].values[0]
def get_title_from_index(df, index):
   return df[df.index == index]['name'].values[0]
def get_index_from_title(df, title):
   return df[df.name == title].index.values[0]
def get_score_from_index(df, index):
   return df[df.index == index]['score'].values[0]
def get_weighted_score_from_index(df, index):
   return df[df.index == index]['weighted_score'].values[0]
def get_total_ratings_from_index(df, index):
   return df[df.index == index]['total_ratings'].values[0]
def get_platform_from_index(df, index):
   return df[df.index == index]['platforms'].values[0]

# A function to return the most similar title to the words a user type
# Without this, the recommender only works when a user enters the exact title which the data has.
def find_closest_title(df, title):
   leven_scores = list(enumerate(df['name'].apply(matching_score, b=title))) #[(0, 30), (1,95), (2, 19)~~] A tuple of distances per index
   sorted_leven_scores = sorted(leven_scores, key=lambda x: x[1], reverse=True) #Sorts list of tuples by distance [(1, 95), (3, 49), (0, 30)~~]
   closest_title = get_title_from_index(df, sorted_leven_scores[0][0])
   distance_score = sorted_leven_scores[0][1]
   return closest_title, distance_score
# returns only one title but I want a dropdown of the 10 closest game titles
def closestNames(title):
   df = pd.DataFrame()
   leven_scores = list(enumerate(df['name'].apply(matching_score, b=title)))
   sorted_leven_scores = sorted(leven_scores, key=lambda x: x[1], reverse=True)
   top_closest_names = [get_title_from_index(i[0]) for i in sorted_leven_scores[:10]]
   return top_closest_names

def updateRecommFirebase(df, matrix):
   # Firebase Credentials
   cred = credentials.Certificate("wdips-functions\wdips-creds.json")
   app = firebase_admin.initialize_app(cred)
   db = firestore.client()
   
   # For loop to go through each game in the similarity matrix
   for r in range(0,len(matrix)):
      #Extract the list (row) of similar games in the matrix in index r to a tuple.
      row = list(enumerate(matrix[int(r)]))
      #Sort the list of tuples by the similarity score
      row_sorted = list(filter(lambda x:x[0] != int(r), sorted(row,key=lambda x:x[1], reverse=True)))
      #Extract only the indexes if the sorted list
      idxList = list(zip(*row_sorted))[0]
      
      #Extract the appid of the game in the current row
      currAppID = get_appid_from_index(df, row[r][0])
      
      #Create Dictionary with the appid of the current game and the list of (100) similar games
      topRecDict = {'appID': str(currAppID), 'topRecommend': {}}
      for g in range(0,100):
         #Add the 100 most simalar games to the dictionary
         topRecDict['topRecommend'].update({str(g+1): str(get_appid_from_index(df, idxList[g]))})
      
      #Add the dictionary to the firebase database
      doc_ref = db.collection(u'recommendation').document(u'' + str(currAppID))
      doc_ref.set(topRecDict, merge=True)
   
    
def recommend(df, how_many, dropdown_option, sort_option, min_year, platform, min_score, sm_matrix):
   #Return closest game title match
   closest_title, distance_score = find_closest_title(df, dropdown_option)
   #Create a Dataframe with these column headers
   recomm_df = pd.DataFrame(columns=['Game Title', 'Year', 'Score', 'Weighted Score', 'Total Ratings'])
   #Make the closest title whichever dropdown option the user has chosen
   closest_title = dropdown_option
   #find the corresponding index of the game title
   games_index = get_index_from_title(df, closest_title)
   #return a list of the most similar game indexes as a list
   games_list = list(enumerate(sm_matrix[int(games_index)]))
   #Sort list of similar games from top to bottom
   similar_games = list(filter(lambda x:x[0] != int(games_index), sorted(games_list,key=lambda x:x[1], reverse=True)))
   #Print the game title the similarity matrix is based on
   print('Here\'s the list of games similar to ' + str(closest_title) + ':\n')
   #Only return the games that are on selected platform
   n_games = []
   #for i in range(0, 6169):
      #print(str(i) + "-" + str(similar_games[i][0]))
      
   for i,s in similar_games:
      if platform in get_platform_from_index(df, i):
         n_games.append((i,s))
   #Only return the games that are above the minimum score
   high_scores = []
   for i,s in n_games:
      if get_score_from_index(df, i) > min_score:
         high_scores.append((i,s))
         
   n_games_min_years = []        
   for i,s in n_games:
      if get_title_year_from_index(df, i) >= min_year:
         n_games_min_years.append((i,s))
   #Return the game tuple (game index, game distance score) and store in a dataframe
   for i,s in n_games_min_years[:how_many]:
      #Dataframe will contain attributes based on game index
      row = pd.DataFrame({'Game Title': get_title_from_index(df, i), 'Year': get_title_year_from_index(df, i), 'Score': get_score_from_index(df, i), 'Weighted Score': get_weighted_score_from_index(df, i), 'Total Ratings': get_total_ratings_from_index(df,i)}, index = [0])
      #Append each row to this dataframe
      recomm_df = pd.concat([row, recomm_df])
      #recomm_df = recomm_df.concat(row, ignore_index = True)
   #Sort dataframe by Sort_Option provided by 
   recomm_df = recomm_df.sort_values(sort_option, ascending=False)
   #Only include games released same or after minimum year 
   #recomm_df = recomm_df[recomm_df['Year'] >= min_year]
   return recomm_df

if __name__ == '__main__':
   # Apply the PreProcess functions to the dataset
   dataDF = PreProcess.importData("Data\steam.csv")
   dataDF = PreProcess.dropNoPlayRimeRows(dataDF)
   dataDF['year'] = dataDF['release_date'].apply(PreProcess.extractYear)
   dataDF = PreProcess.addScoreAndTotalRatings(dataDF)
   dataDF = PreProcess.addWeightedRating(dataDF)
   dataDF = PreProcess.formatColumns(dataDF)
   dataDF = PreProcess.dropNoNameDevPub(dataDF)
   
   #Export the processed data to a csv file
   dataDF.to_csv('Data\cleanedData.csv', index=False)
   
   # create an object for TfidfVectorizer
   tfidfVector = TfidfVectorizer(stop_words='english')

   # convert the list of documents (rows of genre tags) into a matrix
   tfidfMatrix = tfidfVector.fit_transform(dataDF['merged'])
   
   # create the cosine similarity matrix
   sim_matrix = linear_kernel(tfidfMatrix,tfidfMatrix)
   
   ## Call to update the recommendation database in Firebase
   # updateRecommFirebase(dataDF, sim_matrix)
   
   #Get the recommendation with some filters
   result = recommend(dataDF, 10, "Counter-Strike", "Weighted Score", 2000, "windows", 0, sim_matrix)
   print(result)