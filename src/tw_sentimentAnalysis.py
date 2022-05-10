#!/usr/bin/env python3

# IMPORTS
# General:
import tweepy           # To consume Twitter's API
import pandas as pd     # To handle data
import numpy as np      # For number computing

# For plotting and visualization:
from IPython.display import display
import matplotlib.pyplot as plt
#import seaborn as sns

# For sentiment analysis
from textblob import TextBlob #TextBlob, Bayes
import re
import nltk
from textblob.classifiers import NaiveBayesClassifier #Bayes
from textblob.sentiments import NaiveBayesAnalyzer #Bayes
from textblob import Blobber #Bayes
from transformers import AutoTokenizer, AutoModelForSequenceClassification #BERT
import torch #BERT
import requests #BERT
from bs4 import BeautifulSoup #BERT

# JSON and Time
import json
import time
import os

def cleaned(text):
    text = text.translate({ord(c): " " for c in "`'\"[]{}\\"})
    return text

#Tweet Properties: https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet
def jsonTweetGenerator(t):
    _newTweet = {
        "created_at":str(t.created_at),
        "id":t.id,
        "text":cleaned(t.text),
        "source":t.source,
        "truncated":t.truncated,
        "user_id":t.user.id,
        "is_quote_status":t.is_quote_status,
        "retweeted":t.retweeted,
    }
    if hasattr(t, "in_reply_to_status_id"):
        _newTweet["in_reply_to_status_id"] = t.in_reply_to_status_id
        
    if hasattr(t, "in_reply_to_user_id"):
        _newTweet["in_reply_to_user_id"] = t.in_reply_to_user_id
            
    if hasattr(t, "coordinates"):
        _newTweet["coordinates"] = str(t.coordinates)
    
    if hasattr(t, "place"):
        _newTweet["place"] = str(t.place)
    
    if hasattr(t, "favorite_count"):
        _newTweet["favorite_count"] = t.favorite_count
    
    if hasattr(t, "favorited"):
        _newTweet["favorited"] = t.favorited
    
    if hasattr(t, "possibly_sensitive"):
        _newTweet["possibly_sensitive"] = t.possibly_sensitive

    return _newTweet

# TWEET EXTRACTOR FUNCTION (API v1.1)
# This function extract the last 'n' tweets from each user in the input uList and saves the resulting dictionary to a .json file
def tweetExtractor(uList, api_v1):
    out = []
    _path="./out/twitter/usersTweets.json"
    with open(_path, 'w') as outFile:
        outFile.write("[\n")

    for u in range(len(uList)):
        _tweets = []
        try:
            _tweets = api_v1.user_timeline(screen_name=uList[u]["screen_name"], count=100)
            print("{} - Number of tweets extracted for {} is: {}".format(u, uList[u]["screen_name"], len(_tweets)))
            
            json_tweets = []
            for t in _tweets:
                _newTweet = jsonTweetGenerator(t)
                json_tweets.append(_newTweet)
                
            tmp = {"user":uList[u], "tweets":json_tweets}
            out.append(tmp)
            
            with open(_path, 'a') as outFile: #Save to out/outFile
                json.dump({"user":uList[u], "tweets":json_tweets}, outFile)
                outFile.write(",\n")
        
        except Exception as e:
            print(e)
            time.sleep(60*5) #Sleep for 5 minutes
            u = u-1
    
    with open(_path, 'rb+') as filehandle: # remove the last 2 characters ',' and '\n'
            filehandle.seek(-1, os.SEEK_END)
            filehandle.truncate()
            filehandle.seek(-1, os.SEEK_END)
            filehandle.truncate()
    with open(_path, 'a') as outFile:
        outFile.write("\n]")

    return out

# MULTI KEY version of the tweetExtractor FUNCTION (2x API v1.1)
def tweetExtractor_multi(uList, api_v1, api2_v1):
    out = []
    _path="./out/twitter/usersTweets.json"
    with open(_path, 'w') as outFile:
        outFile.write("[\n")

    key1 = True
    for u in range(len(uList)):
        _tweets = []
        if key1:
            try:
                _tweets = api_v1.user_timeline(screen_name=uList[u]["screen_name"], count=100)
                print("{} - Number of tweets extracted for {} is: {}".format(u, uList[u]["screen_name"], len(_tweets)))
                
                json_tweets = []
                for t in _tweets:
                    _newTweet = jsonTweetGenerator(t)
                    json_tweets.append(_newTweet)
                    
                tmp = {"user":uList[u], "tweets":json_tweets}
                out.append(tmp)
                
                with open(_path, 'a') as outFile: #Save to out/outFile
                    json.dump({"user":uList[u], "tweets":json_tweets}, outFile)
                    outFile.write(",\n")
            
            except Exception as e:
                key1 = False
                print(e)
                print("\nKey1 exhausted!\nSwitching to Key2...")
        else:
            try:
                _tweets = api2_v1.user_timeline(screen_name=uList[u]["screen_name"], count=100)
                print("{} - Number of tweets extracted for {} is: {}".format(u, uList[u]["screen_name"], len(_tweets)))
                
                json_tweets = []
                for t in _tweets:
                    _newTweet = jsonTweetGenerator(t)
                    json_tweets.append(_newTweet)
                    
                tmp = {"user":uList[u], "tweets":json_tweets}
                out.append(tmp)
                
                with open(_path, 'a') as outFile: #Save to out/outFile
                    json.dump({"user":uList[u], "tweets":json_tweets}, outFile)
                    outFile.write(",\n")

            except Exception as e2:
                print(e2)
                print("\nKey2 exhausted!\nSwitching to Key1 AND waiting for 5 minutes...")
                key1 = True
                time.sleep(60*5+2) #Sleep for 5 minutes
                u = u-1
    
    with open(_path, 'rb+') as filehandle: # remove the last 2 characters ',' and '\n'
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
    with open(_path, 'a') as outFile:
        outFile.write("\n]")

    return out


# CLEAN TWEET FUNCTION
# utility function to clean the text by removing links and special characters
def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ANALYZE SENTIMENT FUNCTIONS

# TEXTBLOB
# This function analyses the text of the input tweet and returns the sentiment score of that tweet
#
# NB: We are only assigning values of -1, 0, 1 to the tweet!!! If we want to gather the top 'n%' tweets of the user we will have to do better!
def analyzeSentiment_textBlob(tweet):
    score = -100
    if tweet=="":
        return -50 #Default return value if the tweet is empty

    analysis = TextBlob(clean_tweet(tweet))
    if analysis.sentiment.polarity > 0:
        score = 1
    elif analysis.sentiment.polarity == 0:
        score = 0
    else:
        score = -1

    return score

def analyzeSentiment_naiveBayes(tweet):
    nltk.download('movie_reviews')
    nltk.download('punkt')
    _tb = Blobber(analyzer=NaiveBayesAnalyzer())
    score = -100

    if _tb(tweet).sentiment.classification=="neg":
        score = -1
    elif _tb(tweet).sentiment.classification=="pos":
        score = 1
    else:
        score = 0

    return score

def analyzeSentiment_BERT(tweet):
    score = -100
    tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
    model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

    tokens = tokenizer.encode(tweet, return_tensors='pt')
    result = model(tokens)
    score = int(torch.argmax(result.logits))+1
    return score

# END of sentiment analysis functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# SENTIMENT ANALYSIS FUNCTION (API v1.1)
# This function analyses the input tweets and pairs them with a sentiment analysis score
def sentimentAnalysis(tList, method):
    out = []
    _path="./out/twitter/analyzedUsersTweets_v2.json"
    if tList==[]:
        print("Sentiment Analysis Exception: Empty List!!!")
        return []

    with open(_path, 'w') as outFile:
        outFile.write("[\n")


    for user in tList:
        print("analyzing {} ".format(user["user"]["name"]))
        newTweets = []
        for tweet in user["tweets"]:
            score = -100
            if method=="textBlob":
                score = analyzeSentiment_textBlob(tweet["text"])
            elif method=="bayes":
                score = analyzeSentiment_naiveBayes(tweet["text"])
            elif method=="bert":
                score = analyzeSentiment_BERT(tweet["text"])
            else:
                print("\nFATAL: This method does not exist!")

            newTweets.append((tweet,score))
        
        tmp = {"user":user["user"], "tweets":newTweets}
        out.append(tmp)
        
        with open(_path, 'a') as outFile: #Save to out/outFile
            json.dump({"user":user["user"], "tweets":newTweets}, outFile)
            outFile.write(",\n")

    with open(_path, 'rb+') as filehandle: # remove the last 2 characters ',' and '\n'
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
    with open(_path, 'a') as outFile:
        outFile.write("\n]")

    return out

# SENTIMENT ANALYSIS FUNCTION (API v1.1) [w/ FILE BASED INPUT]
# This function analyses the input tweets and pairs them with a sentiment analysis score
def sentimentAnalysis_file(tFile="./out/twitter/usersTweets.json"):
    out = []
    tList = []
    
    with open(tFile, 'r') as inFile:
        tList = json.load(inFile)
    if not(tList):
        print("\nTweet list is EMPTY, input: {}\n".format(tFile))

    return sentimentAnalysis(tList)

