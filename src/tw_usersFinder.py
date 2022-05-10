#!/usr/bin/env python3

#IMPORTS
import json
import tweepy
import time

# JSON USER FUNCTION
# this function takes in input a Twitter 'GET/User' object and transforms it into a custom json version
def jsonUserGenerator(user):
    _newUser = {
        "id":user.id,
        "name":user.name,
        "screen_name":user.screen_name,
        "protected":user.protected,
        "verified":user.verified,
        "followers_count":user.followers_count,
        "friends_count":user.friends_count,
        "statuses_count":user.statuses_count,
        "created_at":str(user.created_at),
        "profile_image_url_https":str(user.profile_image_url_https),
        "default_profile":user.default_profile
    }
    if hasattr(user, "location"):
        _newUser["location"] = user.location
    if hasattr(user, "url"):
        _newUser["url"] = user.url
    if hasattr(user, "description"):
        _newUser["description"] = user.description

    return _newUser

# FIND function (API v1.1)
# this function takes in input a List containing all the users it needs to find with the Twitter search function and returns a list of said users as 'user' objects
def findAllUsers(users_to_find, api_v1, manual=False):
    out = []
    json_out = []
    if users_to_find==[]:
        print("\n--------------------\n")
        print("The input list is empty!\n")
        return out

    #for user in users_to_find:
    for u in range(len(users_to_find)):
        try:
            # use the API to find all the users associated with the current user's name and append them to "out"
            print("Searching for "+str(users_to_find[u])) #Debug
            if manual: #Only gathers the FIRST (and correct) result
                out = out + [api_v1.search_users(users_to_find[u]["name"])[0]]
            else: 
                out = out + api_v1.search_users(users_to_find[u]["name"])
        except tweepy.errors.TooManyRequests as e:
            print(e)
            time.sleep(60*5) #Sleep for 5 minutes
            u = u-1
    
    #SAVE the found Users (in json format)
    for u in out:
        json_out.append(jsonUserGenerator(u))
    with open("./out/twitter/usersList.json", 'w') as outFile:
        json.dump(json_out, outFile)

    return json_out

# MULTI KEY version of findAllUsers FUNCTION (2x API v1.1)
def findAllUsers_multi(users_to_find, api_v1, api2_v1, manual=False):
    out = []
    json_out = []
    if users_to_find==[]:
        print("\n--------------------\n")
        print("The input list is empty!\n")
        return out

    #for user in users_to_find:
    key1 = True
    for u in range(len(users_to_find)):
        if key1:
            try:
                # use the API to find all the users associated with the current user's name and append them to "out"
                print("Searching for "+str(users_to_find[u])) #Debug
                if manual: #Only gathers the FIRST (and correct) result
                    out = out + [api_v1.search_users(users_to_find[u]["name"])[0]]
                else: 
                    out = out + api_v1.search_users(users_to_find[u]["name"])
            #except Exception as e:
            except tweepy.errors.TooManyRequests as e:
                key1 = False
                print(e)
                print("Key1 exhausted!\nSwitching to Key2...\n")
                
        else:
            try:
                # use the API to find all the users associated with the current user's name and append them to "out"
                print("Searching for "+str(users_to_find[u])) #Debug
                if manual: #Only gathers the FIRST (and correct) result
                    out = out + [api2_v1.search_users(users_to_find[u]["name"])[0]]
                else: 
                    out = out + api2_v1.search_users(users_to_find[u]["name"])

            except tweepy.errors.TooManyRequests as e2:
                print(e2)
                print("Key2 exhausted!\nSwitching to Key1 AND waiting for 5 minutes...")
                key1 = True
                time.sleep(60*5+2) #Sleep for 5 minutes
                u = u-1
    
    #SAVE the found Users (in json format)
    for u in out:
        json_out.append(jsonUserGenerator(u))
    with open("./out/twitter/usersList.json", 'w') as outFile:
        json.dump(json_out, outFile)

    return json_out

# FINDRELATIONSHIPS FUNCTION (API v1.1)
# this functions takes in input a list containing tweepy Users and returns a list of dictionaries each containing a user, it's followed users and it's followers
def findRelationships(uList, api_v1):
    out = []
    t1 = []
    t2 = []

    for u in range(len(uList)):
        _followerList = []
        try:
            _followerList = api_v1.get_follower_ids(user_id=uList[u]["id"], count=200)
            print("{} - Number of followers extracted for {} is {}".format(u, uList[u]["screen_name"], len(_followerList)))
            t1.append({"user":uList[u], "followers":_followerList})

        except Exception as e:
            print(e)
            time.sleep(60*5) #Sleep for 5 minutes
            u = u-1

    for u in range(len(uList)):
        _followedList = []
        try:
            _followedList = api_v1.get_friend_ids(user_id=uList[u]["id"], count=200)
            print("{} - Number of followed users extracted for {} is {}".format(u, uList[u]["screen_name"], len(_followedList)))
            t2.append({"user_id":uList[u]["id"], "followed":_followedList})
            
        except Exception as e:
            print(e)
            time.sleep(60*5+2) #Sleep for 5 minutes
            u = u-1

    for u1 in t1:
        for u2 in t2:
            if u1["user"]["id"]==u2["user_id"]:
                out.append({"user":u1["user"], "followers":u1["followers"], "followed":u2["followed"]})

    with open("./out/twitter/usersRelationships.json", 'w') as outFile:
        json.dump(out, outFile)

    return out

# MULTI KEY version of findRelationships() FUNCTION (2x API v1.1)
def findRelationships_multi(uList, api1_v1, api2_v1):
    out = []
    t1 = []
    t2 = []

    key1 = True
    for u in range(len(uList)):
        _followerList = []
        if key1:
            try:
                _followerList = api1_v1.get_follower_ids(user_id=uList[u]["id"], count=200)
                print("{} - Number of followers extracted for {} is {}".format(u, uList[u]["screen_name"], len(_followerList)))
                t1.append({"user":uList[u], "followers":_followerList})

            except Exception as e:
                key1 = False
                print(e)
                print("Key1 exhausted!\nSwitching to Key2...\n")
        else:
            try:
                _followerList = api2_v1.get_follower_ids(user_id=uList[u]["id"], count=200)
                print("{} - Number of followers extracted for {} is {}".format(u, uList[u]["screen_name"], len(_followerList)))
                t1.append({"user":uList[u], "followers":_followerList})
                
            except Exception as e2:
                key1 = True
                print(e2)
                print("Key2 exhausted!\nStwitching to Key1 AND waiting for 5 minutes...")
                time.sleep(60*5+2) #Sleep for 5 minutes
                u = u-1

    key1 = True
    for u in range(len(uList)):
        _followedList = []
        if key1:
            try:
                _followedList = api1_v1.get_friend_ids(user_id=uList[u]["id"], count=200)
                print("{} - Number of followed users extracted for {} is {}".format(u, uList[u]["screen_name"], len(_followedList)))
                t2.append({"user_id":uList[u]["id"], "followed":_followedList})
                
            except Exception as e:
                key1 = False
                print(e)
                print("Key1 exhausted!\nSwitching to Key2...\n")
        else:
            try:
                _followedList = api2_v1.get_friend_ids(user_id=uList[u]["id"], count=200)
                print("{} - Number of followed users extracted for {} is {}".format(u, uList[u]["screen_name"], len(_followedList)))
                t2.append({"user_id":uList[u]["id"], "followed":_followedList})
                
            except Exception as e2:
                key1 = True
                print(e2)
                print("Key2 exhausted!\nSwitching to Key1 AND waiting for 5 minutes...")
                time.sleep(60*5+2) #Sleep for 5 minutes
                u = u-1

    for u1 in t1:
        for u2 in t2:
            if u1["user"]["id"]==u2["user_id"]:
                out.append({"user":u1["user"], "followers":u1["followers"], "followed":u2["followed"]})

    with open("./out/twitter/usersRelationships.json", 'w') as outFile:
        json.dump(out, outFile)

    return out
