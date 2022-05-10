#!/usr/bin/env python3

# IMPORTS
from src import tw_auth
from src import tw_usersFinder
from src import tw_communityDetection
from src import tw_sentimentAnalysis

#--------------------tw_auth--------------------

# ALIAS for auth_v1 FUNCTION 
def auth(config_path="./config_default_tw.json"):
    return tw_auth.auth_v1(config_path)
    
# AUTHENTICATION FUNCTION
# this function uses the config.json file to authenticate with the data provided to the TWITTER APIs to enable API_v1 usage
def auth_v1(config_path="./config_default_tw.json"):
    return tw_auth.auth_v1(config_path)

# AUTHENTICATION FUNCTION
# this function uses the config.json file to authenticate with the data provided to the TWITTER APIs to enable API_v2 usage
def auth_v2(config_path="./config_default_tw.json"):
    return tw_auth.auth_v2(config_path)

#--------------------tw_usersFinder--------------------

# FIND function (API v1.1)
# this function takes in input a List containing all the users it needs to find with the Twitter search function and returns a list of said users as 'user' objects
def findAllUsers(users_to_find, api_v1, manual=False):
    return tw_usersFinder.findAllUsers(users_to_find, api_v1, manual)

# MULTI KEY version of findAllUsers() FUNCTION (2x API v1.1)
def findAllUsers_multi(users_to_find, api1_v1, api2_v1, manual=False):
    return tw_usersFinder.findAllUsers_multi(users_to_find, api1_v1, api2_v1, manual)

# FINDRELATIONSHIPS FUNCTION (API v1.1)
# this functions takes in input a list containing tweepy Users and returns a list of dictionaries each containing a user, it's followed users and it's followers
def findRelationships(uList, api_v1):
    return tw_usersFinder.findRelationships(uList, api_v1)

# MULTI KEY version of findRelationships() FUNCTION (2x API v1.1)
def findRelationships_multi(uList, api1_v1, api2_v1):
    return tw_usersFinder.findRelationships_multi(uList, api1_v1, api2_v1)

#--------------------tw_communityDetection--------------------

# COMMUNITY DETECTION function
# this function takes in input a List containing all the Twitter users as 'user' objects and uses the girvan_newman altorithm to find one or more communities from the users in input. It returns the community found as a list of 'users' that belong to said community
def communityDetection(uList, visual_mode=False):
    return tw_communityDetection.communityDetection(uList, visual_mode)

def communityDetection_file(uList_file="./out/usersRelationships.json", visual_mode=False):
    return tw_communityDetection.communityDetection_file(uList_file, visual_mode)

#DRAW graph function
def draw(community, labels=True):
    return tw_communityDetection.draw(community, labels)

#--------------------tw_sentimentAnalysis--------------------

# TWEET EXTRACTOR FUNCTION (API v1.1)
# This function extract the last 'n' tweets from each user in the input uList and saves the resulting dictionary to a .json file
def tweetExtractor(uList, api_v1):
    return tw_sentimentAnalysis.tweetExtractor(uList, api_v1)

# TWEET EXTRACTOR MULTI FUNCTION (API v1.1)
# This function acts as tweetExtractor but uses two API keys
def tweetExtractor_multi(uList, api_v1, api2_v1):
    return tw_sentimentAnalysis.tweetExtractor_multi(uList, api_v1, api2_v1)

# SENTIMENT ANALYSIS FUNCTION (API v1.1)
# This function analyses the input tweets and pairs them with a sentiment analysis score
def sentimentAnalysis(tList, method="textBlob"):
    return tw_sentimentAnalysis.sentimentAnalysis(tList, method)
