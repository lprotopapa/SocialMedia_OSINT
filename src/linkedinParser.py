#!/usr/bin/env python

#FILENAME: linkedinParser.py

# IMPORTS
import json

# This FUNCTION checks if a given string contains numbers
def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

# This FUNCTION extracts the users from the .har file, returning them in a .json List
def findUsers_ordered(harfile):
    out = [] #Array of users
    dataList = []
    debug_dataCount = 0
    with open(harfile, 'r') as infile:
        for line in infile:
            if(line.find("text")!=-1 and line.find("USER_LOCALE")!=-1 and line.find("badgeText")!=-1 and line.find("https://www.linkedin.com/in/")!=-1):
                dataList.append(line)
                debug_dataCount+=1
        print("\nNumber of Data lines: " + str(debug_dataCount)+"\n")
    
    for data in dataList:
        # Trim the first USER_LOCALE (doesn't refer to a USER)
        data = data[data.find("USER_LOCALE")+11:]
        t0 = data.find("USER_LOCALE")
        while t0!=-1:
            user = {}
            t0 = data.find("USER_LOCALE")
            if (data.find("badgeText")==-1 or data.find("https://www.linkedin.com/in/")==-1):
                    break #NO more users in this data line
            # Skip untill
            while True:
                t0 = data.find("USER_LOCALE")
                t2 = data.find("badgeText")
                tmp = data[t0+10:t2]
                if tmp.find("USER_LOCALE")==-1:
                    data = data[t0-1:]
                    break
                else:
                    data = data[t0+1:]

            # BadgeText
            t0 = data.find("USER_LOCALE")
            t1 = data.find("badgeText")
            userData = data[t0+10:t1]
            if userData.find("USER_LOCALE")==-1 and t1!=-1:
                #extract the text attribute associated to the User's title 
                tmp = userData.split("\\\"")
                userData = tmp[4]
                user["badgeText"] = userData
            else:
                print("Something went wrong!!!")
            data = data[t1:]
            
            # Skip untill
            while True:
                t0 = data.find("USER_LOCALE")
                t2 = data.find("https://www.linkedin.com/in/")
                tmp = data[t0+10:t2-1]
                if tmp.find("USER_LOCALE")==-1:
                    data = data[t0-1:]
                    break
                else:
                    data = data[t0+1:]

            # name+link
            t0 = data.find("USER_LOCALE")
            t3 = data.find("https://www.linkedin.com/in/")
            t4 = data[t3:].find("\\\"")
            if data[t0+10:t4].find("USER_LOCALE")==-1 and t3!=-1:
                userData = data[t3:]
                userData = userData[:t4]
                tmp_link = userData.split("?")
                link = tmp_link[0]
                tmp_name = link.split("-")
                if has_numbers(tmp_name[-1]):
                    name = ' '.join(tmp_name[:-1])
                else:
                    name = ' '.join(tmp_name)
                user["name"] = name.replace("https://www.linkedin.com/in/", "")
                user["link"] = link
            else:
                print("Something went wrong!!!")
            data = data[t3:]
            out.append(user)
        
    #print("RAW Users List:") #debug
    #print(out)
    #print("\n--------------------\n")
    
    # Find wrong/unexisting users
    toDelete = []
    for i in range(len(out)):
        if (not("name" in out[i]) or out[i]['name'] == "" or has_numbers(out[i]['name'])):
            toDelete.append(out[i]) 
    # Remove wrong/unexisting users
    for i in range(len(toDelete)):
        for j in range(len(out)):
            if not("link" in out[j]):
                del out[j]
                break
            elif ("link" in toDelete[i]) and (toDelete[i]['link']==out[j]['link']):
                del out[j]
                break

    #print("Named Users List:") #debug
    #print(out)
    #print("\n--------------------\n")
    
    with open("./out/linkedin/parsedHar.json", 'w') as f:
        json.dump(out, f) #SAVE to .json file
    return out

#This FUNCTION checks if the User's title matches any of the hierarchy titles inside the model
# NB: The model is structured as follws: [["title1","title1.1,..."],["title2"],...,["titleN"]] (a list of lists of Strings)
def matchTitle(user, model):
    for group in model:
        for title in group:
            if user["badgeText"].upper().find(title)!=-1:
                return True
    return False

#This FUNCTION takes in input a USERs LIST and divides it in a hierarchical structure. It outputs a list containing the hierarchical structure as a dictionary and the List of "common" users 
def findHierarchy(userList):
    hierarchyModelStandard = [["PRESIDENT"],["CEO ","CHIEF EXECUTIVE OFFICER"],["CFO ","CHIEF FINANCIAL OFFICER","COO ","CHIEF OPERATING OFFICER","CTO ","CHIEF TECHNICAL OFFICER","CHIEF TECHNOLOGY OFFICER","CIO ","CHIEF INFORMATION OFFICER","CLO ","CHIEF LEGAL OFFICER","CHIEF LEARNING OFFICER","CMO ","CHIEF MARKETING OFFICER","GLOBAL MARKETING OFFICER","CHRO ","CHIEF HR OFFICER","CHIEF HUMAN RESOURCES OFFICER","CPO ","CHIEF PEOPLE OFFICER"],["DIRECTOR"],["MANAGER"],["SUPERVISOR"]]
    #Separate VIP from commoners (by removing commoners from UserList)
    commoners = []
    for user in userList:
        if(not(matchTitle(user, hierarchyModelStandard))):
            commoners.append(user)
    for i in range(len(commoners)):
        for j in range(len(userList)):
            if(userList[j]['link']==commoners[i]['link']):
                del userList[j]
                break

    #Instance an empty model
    hierarchyModel = []
    for i in range(len(hierarchyModelStandard)):
        hierarchyModel.append([])

    #Divide VIPs in the hierarchy
    for user in userList:
        g = 0
        for group in hierarchyModelStandard:
            for title in group:
                if user["badgeText"].upper().find(title)!=-1:
                    hierarchyModel[g].append(user)
            g+=1
    #print("Hierarchy model in LIST format:") #debug
    #print(hierarchyModel)
    #print("\n--------------------\n")
    
    jsonHierarchyModel = {"CompanyHierarchy":{
        "President(s)":hierarchyModel[0],
        "CEO":hierarchyModel[1],
        "Chiefs":hierarchyModel[2],
        "Director(s)":hierarchyModel[3],
        "Manager(s)":hierarchyModel[4],
        "Supervisor(s)":hierarchyModel[5]
        }
    } 
    #print("Hierarchy model in JSON format:") #debug
    #print(jsonHierarchyModel)
    #print("\n--------------------\n")
    
    #SAVE output as .json files
    with open("./out/linkedin/userHierarchyList.json", 'w') as f:
        json.dump(hierarchyModel, f) #SAVE as .json file
    with open("./out/linkedin/userHierarchy.json", 'w') as f:
        json.dump(jsonHierarchyModel, f)

    return {"VIPs" : jsonHierarchyModel, "commoners" : commoners}

# This FUNCTION adds the "flagged" property to any users that could be of interest
def findFlags(usersModel):
    for u in usersModel["VIPs"]["CompanyHierarchy"]["President(s)"]:
        if u["badgeText"].lower().find("admin")!=-1 or u["badgeText"].lower().find("cloud")!=-1 or u["badgeText"].lower().find("security")!=-1:
            u["flagged"] = True
        else:
            u["flagged"] = False
    for u in usersModel["VIPs"]["CompanyHierarchy"]["CEO"]:
        if u["badgeText"].lower().find("admin")!=-1 or u["badgeText"].lower().find("cloud")!=-1 or u["badgeText"].lower().find("security")!=-1:
            u["flagged"] = True
        else:
            u["flagged"] = False
    for u in usersModel["VIPs"]["CompanyHierarchy"]["Chiefs"]:
        if u["badgeText"].lower().find("admin")!=-1 or u["badgeText"].lower().find("cloud")!=-1 or u["badgeText"].lower().find("security")!=-1:
            u["flagged"] = True
        else:
            u["flagged"] = False
    for u in usersModel["VIPs"]["CompanyHierarchy"]["Director(s)"]:
        if u["badgeText"].lower().find("admin")!=-1 or u["badgeText"].lower().find("cloud")!=-1 or u["badgeText"].lower().find("security")!=-1:
            u["flagged"] = True
        else:
            u["flagged"] = False
    for u in usersModel["VIPs"]["CompanyHierarchy"]["Manager(s)"]:
        if u["badgeText"].lower().find("admin")!=-1 or u["badgeText"].lower().find("cloud")!=-1 or u["badgeText"].lower().find("security")!=-1:
            u["flagged"] = True
        else:
            u["flagged"] = False
    for u in usersModel["VIPs"]["CompanyHierarchy"]["Supervisor(s)"]:
        if u["badgeText"].lower().find("admin")!=-1 or u["badgeText"].lower().find("cloud")!=-1 or u["badgeText"].lower().find("security")!=-1:
            u["flagged"] = True
        else:
            u["flagged"] = False
    
    for u in usersModel["commoners"]:
        if u["badgeText"].lower().find("admin")!=-1 or u["badgeText"].lower().find("cloud")!=-1 or u["badgeText"].lower().find("security")!=-1:
            u["flagged"] = True
        else:
            u["flagged"] = False
    return usersModel


