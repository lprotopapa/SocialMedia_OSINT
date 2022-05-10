#!/usr/bin/env python3

#TODO: 
#   - (linkedinParser.py) Fix or remove (I am currently removing them) the user's without a correct 'name' (since the linkedin link doesn't contain their name).
#   - (linkedinParser.py) Fix or remove (I am currently removing them) the users without a 'name' field or 'link' (problems with parsing or the .har file?!)
#
#   ---> NB: theese users might be valid and useful users but we can't extract the name so we can't proceed with further analysis (eg. twitter) [INVESTIGATE]
#

# IMPORTS
# General imports
import json
import sys, os
import argparse
import time

# Project files
from src import linkedinParser as lkp
from src import twitter_handler as tw
#import tw_auth
#import tw_usersFinder
#import tw_communityDetection
#import tw_sentimentAnalysis

#import twintAnalysisTool as twat # ONLY IF CONFIG

def extractVIPs(VIPs):
    out = []
    for u in VIPs["CompanyHierarchy"]["President(s)"]:
        out.append(u)
    for u in VIPs["CompanyHierarchy"]["CEO"]:
        out.append(u)
    for u in VIPs["CompanyHierarchy"]["Chiefs"]:
        out.append(u)
    for u in VIPs["CompanyHierarchy"]["Director(s)"]:
        out.append(u)
    for u in VIPs["CompanyHierarchy"]["Manager(s)"]:
        out.append(u)
    for u in VIPs["CompanyHierarchy"]["Supervisor(s)"]:
        out.append(u)

    return out

# ---------- MAIN ----------
def main(argv):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-c", "--config", dest = "config_file", default = "./default_config.json", help = "Path to the configuration file, defaults to './default_config.json'")
    args = arg_parser.parse_args()
    
    print("Configuration file path set to: {}".format(args.config_file))
    config = []
    with open(args.config_file, 'r') as cFile:
        config = json.load(cFile)

    print("Starting parsing process...\n")
    print("\n--------------------\n")
    
    # ---------- LINKEDIN ----------
    # Variables
    users_to_investigate = []
    if config["linkedin_find_users"]:
        if config["linkedin_scrape_mode"] and config["linkedin_har_file"]!="" and config["linkedin_har_file"]!="./Data/har/<input har file>":
            users = lkp.findUsers_ordered(config["linkedin_har_file"])
            users_li = lkp.findHierarchy(users) # {VIPs, commoners}
            users_li = lkp.findFlags(users_li) # {VIPs, commoners}
            
            VIPs = []
            flagged = []
            for u in extractVIPs(users_li["VIPs"]):
                VIPs.append(u["name"])
            for u in users_li["commoners"]:
                if u["flagged"]==True:
                    flagged.append(u["name"])
            users_to_investigate = VIPs + flagged
            print("\nTotal # of VIPs to investigate: {}".format(len(users_to_investigate)))
            print("# of VIPs: {}".format(len(VIPs)))
            print("# of flagged standard users: {}".format(len(flagged)))
            time.sleep(2)
            print("\n--------------------\n")
            
            #TEMPORARY
            with open("./out/linkedin/flagged_standard.json", 'w') as outFile:
                json.dump(flagged, outFile)

    # ---------- TWITTER ----------
    # Variables (excluding APIs)
    manual_targets = []
    tw_users = []

    # ~~~ AUTH SECTION ~~~
    # Setup twitter API keys
    if config["twitter_key1"]!="" and config["twitter_key1"]!="<path to twitter key config file>":
        print(config["twitter_key1"])
        API_v1 = tw.auth_v1(config["twitter_key1"])
    else:
        print("You MUST provide a valid twitter_key1 in the configuration file!\nclosing...") #error
        sys.exit()

    if config["twitter_key2"]!="" and config["twitter_key2"]!="<path to secondary twitter key config file>":
        if config["twitter_key1"]!=config["twitter_key2"]:
            API2_v1 = tw.auth_v1(config["twitter_key2"])
        else:
            print("The two twitter_key keys must be different!\nclosing...") #error
            sys.exit()
    
    if config["manual_target_mode"] and config["manual_targets_file"]!="./Data/tw_targets/<twitter manual target file>" and config["manual_targets_file"]!="":
        with open(config["manual_targets_file"], 'r') as tFile:
            manual_targets = json.load(tFile)

    if not(config["manual_target_mode"]):
        print("\nThis module can only work in manual target mode for the moment! (The APIs are too slow to gather Users automatically)\nclosing...") #error
        sys.exit()

    for target in manual_targets:
        tw_users.append({"name":target["twitter"][0]})
    
    if config["twitter_target"]!="" and config["twitter_target"]!="<main twitter target>":
        tw_users.append({"name":config["twitter_target"]})
    else:
        print("You MUST provide a valid twitter_target in the configuration file!\nclosing...") #error
        sys.exit()
    # ~~~ end of AUTH section ~~~

    #FIND USERS (consumes key uses)
    _path = "./out/twitter/usersList.json"
    if config["twitter_find_users"]:
        if config["multi_key"]:
            tw_users = tw.findAllUsers_multi(tw_users, API_v1, API2_v1, config["manual_target_mode"])
        else:
            tw_users = tw.findAllUsers(tw_users, API_v1, config["manual_target_mode"])
    elif os.path.exists(_path):
        with open(_path, 'r') as inFile:
            print("loading Twitter users file...")
            tw_users = json.load(inFile)
    else:
        print("WARNING: no users file in {}".format(_path))

    print("Twitter targets found:")
    for u in tw_users:
        print(u["name"])
    print("\n--------------------\n")

    #EXTRACT RELATIONS (consumes key uses)
    _path = "./out/twitter/usersRelationships.json"
    tw_relations = []
    if config["twitter_find_relationships"]:
        if config["multi_key"]:
            tw_relations = tw.findRelationships_multi(tw_users, API_v1, API2_v1)
        else:
            tw_relations = tw.findRelationships(tw_users, API_v1)
        print("ALL relationships found!!!\n")
    elif os.path.exists(_path):
        with open(_path, 'r') as inFile:
            print("loading users relationships file...")
            tw_relations = json.load(inFile)
    else:
        print("WARNING: no relations file in {}".format(_path))

    #COMMUNITY DETECTION [VISUAL_OUTPUT !]
    _path = "./out/twitter/?????"
    community = {}
    if config["twitter_community_detection"]:
        community = tw.communityDetection(tw_relations, config["visual_output"])
    elif os.path.exists(_path):
        with open(_path, 'r') as inFile:
            print("loading community file...")
            #community = json.load(inFile)
    else:
        print("WARNING: no community file in {}".format(_path))

    #EXTRACT TWEETS (consumes key ueses)
    _path = "./out/twitter/usersTweets.json"
    tweet_list = []
    if config["twitter_find_tweets"]:
        if config["multi_key"]:
            tweet_list = tw.tweetExtractor_multi(tw_users, API_v1, API2_v1)
        else:
            tweet_list = tw.tweetExtractor(tw_users, API_v1)
    elif os.path.exists(_path):
        with open(_path, 'r') as inFile:
            print("loading users tweets...")
            tweet_list = json.load(inFile)
    else:
        print("WARNING: no tweet file in {}".format(_path))

    #SENTIMENT ANALYSIS
    _path = "./out/twitter/analyzedUsersTweets_v2.json"
    analyzed_tweets = []
    if config["twitter_sentiment_analysis"]:
        analyzed_tweets = tw.sentimentAnalysis(tweet_list, "textBlob")
    elif os.path.exists(_path):
        with open(_path, 'r') as inFile:
            print("loading sentiment analysis results...")
            sentiment_analysis_results = json.load(inFile)
    else:
        print("WARNING: no sentiment analysis file in {}".format(_path))
    
    if analyzed_tweets:
        for t in analyzed_tweets[0]["tweets"]:
            if t[1]==-100 or t[1]==-50:
                print("{} -scored- {}".format(t[0],t[1]))

    #Visualization
    if config["visual_output"]:
        if community:
            print("\n--------------------\n")
            print("Visualizing communities...\n")
            print(community["groups"])
            tw.draw(community, labels=True)

# Execute MAIN
if __name__ == "__main__":
    main(sys.argv[1:])

