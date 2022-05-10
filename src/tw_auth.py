#!/usr/bin/env python3

#IMPORTS
import json
import tweepy

# VALIDATOR FUNCTION
# Takes in input an 'auth' dictionary based on a tw_config file and returns True if it's valid, False otherwise
def config_validator(config):
    default_msg = "INSERT YOUR KEY HERE"
    if (config["consumer_key"]==default_msg or config["consumer_key"]=="")or(config["consumer_secret"]==default_msg or config["consumer_secret"]=="")or(config["access_token"]==default_msg or config["access_token"]=="")or(config["access_token_secret"]==default_msg or config["access_token_secret"]=="")or(config["bearer_token"]==default_msg or config["bearer_token"]==""):
        return False
    else:
        return True

# ALIAS for auth_v1 FUNCTION 
def auth(config_path="./config_default_tw.json"):
    return auth_v1(config_path)

# AUTHENTICATION FUNCTION
# this function uses the config.json file to authenticate with the data provided to the TWITTER APIs to enable API_v1 usage
def auth_v1(config_path="./config_default_tw.json"):

    # read the config file
    config = {}
    with open(config_path, 'r') as c:
        config = json.load(c)

    if(config_validator(config)):
        # get AUTH and API objects
        auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
        auth.set_access_token(config["access_token"], config["access_token_secret"])
        api = tweepy.API(auth)
        return api
    else:
        return None

    return None

# AUTHENTICATION FUNCTION
# this function uses the config.json file to authenticate with the data provided to the TWITTER APIs to enable API_v2 usage
def auth_v2(config_path="./config_default_tw.json"):

    # read the config file
    config = {}
    with open(config_path, 'r') as c:
        config = json.load(c)

    # check if the configuration has been updated
    if(config_validator(config)):
        # get AUTH and API objects
        client_obj = tweepy.Client(config["bearer_token"], config["consumer_key"], config["consumer_secret"], config["access_token"], config["access_token_secret"])
        return client_obj
    else:
        return None

    return None
