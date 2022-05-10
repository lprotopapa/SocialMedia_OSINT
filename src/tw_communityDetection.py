#!/usr/bin/env python3

#IMPORTS
import json
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.community.centrality import girvan_newman

# COMMUNITY DETECTION function
# this function takes in input a List containing all the Twitter users as 'user' objects and uses the girvan_newman altorithm to find one or more communities from the users in input. It returns the community found as a list of 'users' that belong to said community
def communityDetection(uList, visual_mode=False):
    out = []
    if uList==[]:
        print("\n--------------------\n")
        print("The input list is empty!\n")
        return None

    users_tmp = uList
    E = []
    V = []
    for user in uList:
        #print("Searching for "+str(user["user"].name)+" connections") #Debug
        V.append(user["user"]["id"])
        users_tmp.remove(user)

        # find the relationships between user and every other user
        for u2 in users_tmp:
            for i in user["followed"]:
                if u2["user"]["id"]==i: #if the ids match
                    E.append((user["user"]["id"], u2["user"]["id"]))
                    break
            for i in user["followers"]:
                if u2["user"]["id"]==i: #if the ids match
                    E.append((u2["user"]["id"], user["user"]["id"]))
                    break

    # Build the graph
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(E)

    # Apply Girvan Newman
    communities = girvan_newman(G)

    node_groups = []
    for com in next(communities):
        node_groups.append(list(com))
        print(node_groups)
    '''
        color_map = []
        for node in G:
            if node in node_groups[0]:
                color_map.append('blue')
            else:
                color_map.append('green')  
        
    visual_override = True
    if visual_mode and not(visual_override):
        nx.draw(G, node_color=color_map, with_labels=True)
        plt.show()
    '''
    #out = node_groups[0] #FIND the correct node_group somehow! (the one who contains the official FIRM account?)
    out = {"graph":G, "groups":node_groups}
    return out

# DRAW FUNCTION
def draw(community, labels=True):
    color_palette = ["blue","red","darkorange","magenta","gold","blueviolet","olive","lime","aquamarine","cyan","deepskyblue","hotpink","darkred","lightsalmon","yellow"]
    color_map = []
    for node in community["graph"]:
        for i in range(len(community["groups"])):
            if node in community["groups"][i]:
                _found = True
                if i >= len(color_palette):
                    color_map.append("silver")
                else:
                    color_map.append(color_palette[i])
    nx.draw(community["graph"], node_color=color_map, with_labels=labels)
    plt.show()
    
    return 0


# COMMUNITY DETECTION w/ FILE INPUT FUNCTION
# loads the input file and passes it to the main community detection function
def communitydetection_file(uList_file="./out/twitter/userRelationships.json", visual_mode=False):
    uList = []
    with open(uList_file, 'r') as inFile:
        uList = json.load(inFile)
    
    if not(uList):
        print("The user list loaded from {} is EMPTY!!!".format(uList_file))
    
    return communityDetection(uList, visual_mode)
