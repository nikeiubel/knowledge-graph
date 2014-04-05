import json, sys, string, urllib, urllib2, re, collections
from sys import stdout

#Freebase API key = AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs

def main(key, option, query, response):
    if option == '-q':                          #Checks if there is a single query
        if response == 'infobox':
            query_freebase_search(query,key)
        elif response == 'question':
            answer_query(query,key)
        else:
            usage()
    elif option == '-f':                        #Checks if queries are given in a file
        f = open(query, 'r')                    #Opens the file
        if response == 'infobox':
            for line in f:                      #Runs appropriate program for each line of file
                print "\n" + line
                query_freebase_search(line,key)
        elif response == 'question':
            for line in f:
                print "\n\n\nQuery-Question: " + line + "\n\n\n"
                answer_query(line,key)
        else:
            usage()

def query_freebase_search(query, key):
    q = {'query':query, 'key':key}
    url = 'https://www.googleapis.com/freebase/v1/search?' + urllib.urlencode(q)
    req = urllib2.Request(url)   
    content = json.loads(urllib2.urlopen(req).read())
    global entries
    global validEntries
    entries = []
    validEntries = []
    topicResult = dict()
    count = 0
    for obj in content["result"]:
        topicResult = query_freebase_topic(key, obj["mid"])
        if (topicResult): # will stop at the top-level mid containing valid entry
            infobox = output_infobox(topicResult, validEntries)
            if (infobox): 
                return  #quit searching API because relevant results has been found and printed out
            else: 
                count += 1
        else:
            count += 1
        if count%5 == 0:
            print str(count) + " Search API result entries were considered. None of them of a supported type."
        if count > len(content["result"]):
            return

def query_freebase_topic(key, mid):
    url = 'https://www.googleapis.com/freebase/v1/topic'
    params = {
        'key': key,
    }
    url += mid + '?' + urllib.urlencode(params)
    req = urllib2.Request(url)
    topic = json.loads(urllib2.urlopen(req).read())
    for entry in topic["property"]["/type/object/type"]["values"]:
        entries.append(str(entry["id"]))
    validEntities = {"/people/person","/book/author","/film/actor","/tv/tv_actor","/organization/organization_founder","/business/board_member","/sports/sports_league","/sports/sports_team","/sports/professional_sports_team"}
    if any(entry in validEntities for entry in entries):
        for e in entries:
            if e in validEntities:
                validEntries.append(e)
        return topic
    else:
        del entries[:]
        return {}

# prints out infobox
def output_infobox (topicResult, validEntries):
    INFOBOX_LENGTH = 98
    name = topicResult["property"]["/type/object/name"]["values"][0]["value"] #get name of topic
    mappedEntries = map_Entries(validEntries)

    if "PERSON" in mappedEntries or "LEAGUE" in mappedEntries or "SPORTS TEAM" in mappedEntries:

        #prints top row containing title 
        print_dashed_line(INFOBOX_LENGTH) 
        title = name.title() + "(" 
        for entry in mappedEntries:
            if entry != "PERSON":
                title += entry + ","
        title = title[:-1] + ")"
        print "|" + string.center(title,INFOBOX_LENGTH-1) + "|"
        print_dashed_line(INFOBOX_LENGTH)

        nameText = " Name:" + '\t\t\t'
        nameValue = name
        print "|" + nameText + string.ljust(nameValue,INFOBOX_LENGTH-len(nameText.expandtabs())) + "|"
        print_dashed_line(INFOBOX_LENGTH)

        if "PERSON" in mappedEntries:
            bdayTag = "/people/person/spouse_s"
            if "/people/person/date_of_birth" in topicResult["property"]:
                print_list(" Birthday:" + '\t\t', "/people/person/date_of_birth", topicResult, validEntries, INFOBOX_LENGTH, False)
            if "/people/person/place_of_birth" in topicResult["property"]:
                print_list(" Place of Birth:" + '\t', "/people/person/place_of_birth", topicResult, validEntries, INFOBOX_LENGTH, False)
            if "/people/deceased_person/date_of_death" in topicResult["property"]:
                print_death(topicResult, validEntries, INFOBOX_LENGTH)
            if "/common/topic/description" in topicResult["property"]:
                print_description(topicResult, validEntries, INFOBOX_LENGTH)
            if "/people/person/sibling_s" in topicResult["property"]:
                print_twoLevelsDown(" Siblings:" + '\t\t', "/people/person/sibling_s", "/people/sibling_relationship/sibling", topicResult, validEntries, INFOBOX_LENGTH, False)
            if "/people/person/spouse_s" in topicResult["property"]:
                print_spouses(topicResult, validEntries, INFOBOX_LENGTH)

            if "ACTOR" in mappedEntries:
                if "/film/actor/film" in topicResult["property"]:
                    print_films(topicResult, validEntries, INFOBOX_LENGTH)

            if "AUTHOR" in mappedEntries:
                if "/book/author/works_written" in topicResult["property"]:
                    print_list(" Books:" + '\t\t', "/book/author/works_written", topicResult, validEntries, INFOBOX_LENGTH, True)
                if "/influence/influence_node/influenced_by" in topicResult["property"]:
                    print_list(" Influenced By:" + '\t', "/influence/influence_node/influenced_by", topicResult, validEntries, INFOBOX_LENGTH, True)
                if "/book/book_subject/works" in topicResult["property"]:
                    print_list(" Books about:" + '\t\t', "/book/book_subject/works", topicResult, validEntries, INFOBOX_LENGTH, False)
                if "/influence/influence_node/influenced" in topicResult["property"]:
                    print_list(" Influenced:" + '\t\t', "/influence/influence_node/influenced", topicResult, validEntries, INFOBOX_LENGTH, False)
    
            if "BUSINESS" in mappedEntries:
                if "/organization/organization_founder/organizations_founded" in topicResult["property"]:
                    print_list(" Founded:" + '\t\t', "/organization/organization_founder/organizations_founded", topicResult, validEntries, INFOBOX_LENGTH, False)
        
                if "/business/board_member/leader_of" in topicResult["property"]:
                    subTexts = []
                    subTexts.append("Organization") 
                    subTexts.append("Role") 
                    subTexts.append("Title") 
                    subTexts.append("From-To")

                    tagsLeader = []
                    tagsLeader.append("/business/board_member/leader_of")
                    tagsLeader.append("/organization/leadership/organization")
                    tagsLeader.append("/organization/leadership/role")
                    tagsLeader.append("/organization/leadership/title")
                    tagsLeader.append("/organization/leadership/from")
                    tagsLeader.append("/organization/leadership/to")
                    print_bizList(" Leadership:", tagsLeader, subTexts, topicResult, validEntries, INFOBOX_LENGTH, 4)

                if "/business/board_member/organization_board_memberships" in topicResult["property"]:
                    tagsBoard = []
                    tagsBoard.append("/business/board_member/organization_board_memberships")
                    tagsBoard.append("/organization/organization_board_membership/organization")
                    tagsBoard.append("/organization/organization_board_membership/role")
                    tagsBoard.append("/organization/organization_board_membership/title")
                    tagsBoard.append("/organization/organization_board_membership/from")
                    tagsBoard.append("/organization/organization_board_membership/to")
                    print_bizList(" Board Member:", tagsBoard, subTexts, topicResult, validEntries, INFOBOX_LENGTH, 2)

        if "LEAGUE" in mappedEntries:
            if "/sports/sports_league/sport" in topicResult["property"]:
                print_list(" Sport:" + '\t\t', "/sports/sports_league/sport", topicResult, validEntries, INFOBOX_LENGTH, True)
            if "/organization/organization/slogan" in topicResult["property"]:
                print_list(" Slogan:" + '\t\t', "/organization/organization/slogan", topicResult, validEntries, INFOBOX_LENGTH, False)
            if "/common/topic/official_website" in topicResult["property"]:
                print_list(" Official Website:" + '\t',  "/common/topic/official_website", topicResult, validEntries, INFOBOX_LENGTH, False)
            if "/sports/sports_league/championship" in topicResult["property"]:
                print_list(" Championship:" + '\t\t', "/sports/sports_league/championship", topicResult, validEntries, INFOBOX_LENGTH, False)
            if "/sports/sports_league/teams" in topicResult["property"]:
                print_teams(topicResult, validEntries, INFOBOX_LENGTH)
            if "/common/topic/description" in topicResult["property"]:
                print_description(topicResult, validEntries, INFOBOX_LENGTH)

        if "SPORTS TEAM" in mappedEntries:
            print_list(" Sport:" + '\t\t', "/sports/sports_team/sport", topicResult, validEntries, INFOBOX_LENGTH, True)
            print_twoLevelsDown(" Arena:" + '\t\t', "/sports/sports_team/venue", "/sports/team_venue_relationship/venue", topicResult, validEntries, INFOBOX_LENGTH, True)
            print_list(" Championships:" + '\t', "/sports/sports_team/championships", topicResult, validEntries, INFOBOX_LENGTH, True)
            print_list(" Founded:" + '\t\t', "/sports/sports_team/founded", topicResult, validEntries, INFOBOX_LENGTH, False)
            print_twoLevelsDown(" Leagues:" + '\t\t', "/sports/sports_team/league", "/sports/sports_league_participation/league", topicResult, validEntries, INFOBOX_LENGTH, False)
            print_list(" Locations:" + '\t\t', "/sports/sports_team/location", topicResult, validEntries, INFOBOX_LENGTH, False)
        
            subTexts = []
            subTexts.append("Name") 
            subTexts.append("Position")  
            subTexts.append("From-To")
            subTexts.append(" ")

            tagsCoach = []
            tagsCoach.append("/sports/sports_team/coaches")
            tagsCoach.append("/sports/sports_team_coach_tenure/coach")
            tagsCoach.append("/sports/sports_team_coach_tenure/position")
            tagsCoach.append("/sports/sports_team_coach_tenure/from")
            tagsCoach.append("/sports/sports_team_coach_tenure/to")
            tagsCoach.append(" ")
            print_bizList(" Coaches:", tagsCoach, subTexts, topicResult, validEntries, INFOBOX_LENGTH, 8)

            subTexts = []
            subTexts.append("Name") 
            subTexts.append("Position") 
            subTexts.append("Number") 
            subTexts.append("From-To")

            tagsRoster = []
            tagsRoster.append("/sports/sports_team/roster")
            tagsRoster.append("/sports/sports_team_roster/player")
            tagsRoster.append("/sports/sports_team_roster/position")
            tagsRoster.append("/sports/sports_team_roster/number")
            tagsRoster.append("/sports/sports_team_roster/from")
            tagsRoster.append("/sports/sports_team_roster/to")
            print_bizList(" Roster:", tagsRoster, subTexts, topicResult, validEntries, INFOBOX_LENGTH, 8)

            print_description(topicResult, validEntries, INFOBOX_LENGTH)

        return True

    else:
        return False

# generic function to print values of entries (either a simple box or a list)
def print_list(entity, tag, topicResult, validEntries, INFOBOX_LENGTH, tabFixOn):
    tab = '\t'
    if tabFixOn == True:
        i = 1
    else:
        i = 0 
    text = entity
    value = topicResult["property"][tag]["values"]
    step = INFOBOX_LENGTH-len(text.expandtabs())
    value_pieces = []
    for v in value:
        value_pieces.append(v["text"])
    count = 0
    for v in value_pieces:
        if count == 0:
            print "|" + text + string.ljust(v,step-len(tab.expandtabs())*i)[:step] + "|"
        else:
            print "|" + '\t\t\t' + string.ljust(v,step-len(tab.expandtabs())*i)[:step] + "|"
        count += 1
    print_dashed_line(INFOBOX_LENGTH)

# specific function to print values of Teams (SPORTS)
def print_description(topicResult, validEntries, INFOBOX_LENGTH):
    descriptText = " Description:" + '\t\t'
    descriptValue = topicResult["property"]["/common/topic/description"]["values"][0]["value"]
    descriptValue = descriptValue.replace('\n',' ')
    step = INFOBOX_LENGTH-len(descriptText.expandtabs())
    descriptValue_pieces = [descriptValue[i:i+step] for i in range(0, len(descriptValue), step)]
    count = 0
    for d in descriptValue_pieces:
        if count == 0:
            print "|" + descriptText + string.ljust(d,step) + "|"
        else: 
            print "|" + '\t\t\t' + string.ljust(d,step) + "|"
        count += 1
    print_dashed_line(INFOBOX_LENGTH)

# specific function to print values hidden in subtags (two levels down)
def print_twoLevelsDown(entity, maintag, subtag, topicResult, validEntries, INFOBOX_LENGTH, tabFixOn):
    if tabFixOn:
        i = 1
    else:
        i = 0 
    tab = '\t'
    arenaText = entity
    arenaValue = topicResult["property"][maintag]["values"]
    arenaValue_pieces = []
    step = INFOBOX_LENGTH-len(arenaText.expandtabs())
    for d in arenaValue:
        arenaValue_pieces.append(d["property"][subtag]["values"][0]["text"])
    count = 0
    for d in arenaValue_pieces:
        if count == 0:
            print "|" + arenaText + string.ljust(d,step-len(tab.expandtabs())*i) + "|"
        else: 
            print "|" + '\t\t\t' + string.ljust(d,step-len(tab.expandtabs())*i) + "|"
        count += 1
    print_dashed_line(INFOBOX_LENGTH)

# specific function to print values of Death (PERSON)
def print_death(topicResult, validEntries, INFOBOX_LENGTH):  
    tab = '\t'
    text = " Death: " + '\t\t' 
    value = topicResult["property"]["/people/deceased_person/date_of_death"]["values"][0]["text"] + " at " + topicResult["property"]["/people/deceased_person/place_of_death"]["values"][0]["text"] + ", cause: " 
    for t in topicResult["property"]["/people/deceased_person/cause_of_death"]["values"]:
        value += t["text"] + ", "
    value = value[:-2] 
    print "|" + text + string.ljust(value,INFOBOX_LENGTH-len(text.expandtabs())) + "|"
    print_dashed_line(INFOBOX_LENGTH)

# specific function to print values of Spouses (PERSON)
def print_spouses(topicResult, validEntries, INFOBOX_LENGTH):
    spousesText = " Spouses:" + '\t\t'
    spousesValue = topicResult["property"]["/people/person/spouse_s"]["values"]
    spousesValue_spouses = []
    spousesValue_froms = []
    spousesValue_tos = []
    spousesValue_locations = []
    step = INFOBOX_LENGTH-len(spousesText.expandtabs())
    for d in spousesValue:
        if "/people/marriage/spouse" in d["property"]:
            if len(d["property"]["/people/marriage/spouse"]["values"]) > 0:
                spousesValue_spouses.append(d["property"]["/people/marriage/spouse"]["values"][0]["text"])
            else:
                break
        if "/people/marriage/from" in d["property"]:
            if len(d["property"]["/people/marriage/from"]["values"]) > 0:
                spousesValue_froms.append(d["property"]["/people/marriage/from"]["values"][0]["text"])
            else:
                spousesValue_froms.append(" ")
        if "/people/marriage/to" in d["property"]:
            if len(d["property"]["/people/marriage/to"]["values"]) > 0:
                spousesValue_tos.append(d["property"]["/people/marriage/to"]["values"][0]["text"])
            else:
                spousesValue_tos.append("now")
        if "/people/marriage/location_of_ceremony" in d["property"]:
            if len(d["property"]["/people/marriage/location_of_ceremony"]["values"]) > 0:
                spousesValue_locations.append("@ " + d["property"]["/people/marriage/location_of_ceremony"]["values"][0]["text"])
            else:
                spousesValue_locations.append(" ")
    count = 0
    for d in spousesValue_spouses:
        spouseFinalValue = d + " (" + spousesValue_froms[count] + " - " + spousesValue_tos[count] + ") " + spousesValue_locations[count]
        if count == 0:
            print "|" + spousesText + string.ljust(spouseFinalValue,step) + "|"
        else: 
            print "|" + '\t\t\t' + string.ljust(spouseFinalValue,step) + "|"
        count += 1
    print_dashed_line(INFOBOX_LENGTH)

# generic function that prints out lists with multiple values, such as Leadership and Board Member
def print_bizList(entity, tags, subTexts, topicResult, validEntries, INFOBOX_LENGTH, pad):
    text = entity
    subText1 = subTexts[0]
    subText2 = subTexts[1] 
    subText3 = subTexts[2] 
    subText4 = subTexts[3]
    maintag = tags[0]
    subtag1 = tags[1]
    subtag2 = tags[2]
    subtag3 = tags[3]
    subtag4 = tags[4]
    subtag5 = tags[5]
    step = INFOBOX_LENGTH-len(text.expandtabs())
    sublen = step/4-5
    value = topicResult["property"][maintag]["values"]
    value_orgs = []
    value_orgs.append(subText1)
    value_roles = []
    value_roles.append(subText2)
    value_titles = []
    value_titles.append(subText3)
    value_dates = []
    value_dates.append(subText4)
    for v in value:
        if subtag1 in v["property"] and len(v["property"][subtag1]["values"]) > 0:
            value_orgs.append(v["property"][subtag1]["values"][0]["text"])
        else:
            value_orgs.append(" ")
        if subtag2 in v["property"] and len(v["property"][subtag2]["values"]) > 0:
            value_roles.append(v["property"][subtag2]["values"][0]["text"])
        else:
            value_roles.append(" ")
        if subtag3 in v["property"] and len(v["property"][subtag3]["values"]) > 0:
            value_titles.append(v["property"][subtag3]["values"][0]["text"])
        else:
            value_titles.append(" ")
        if subtag4 in v["property"] and len(v["property"][subtag4]["values"]) > 0:
            fromstr = v["property"][subtag4]["values"][0]["text"]
            if subtag5 in v["property"] and len(v["property"][subtag5]["values"]) > 0:
                tostr = v["property"][subtag5]["values"][0]["text"]
            else:
                tostr = "now"
            value_dates.append("(" + fromstr + " / " + tostr + ")") 
        else:
            value_dates.append(" ")
    count = 0
    tab = '\t'
    for v in value_orgs:
        finalValue = "| " + string.ljust(v[:sublen],sublen)  + "| " + string.ljust(value_roles[count][:sublen], sublen)  + "| " + string.ljust(value_titles[count][:sublen], sublen)  + "| " + string.ljust(value_dates[count][:sublen], sublen)
        if count == 0:
            print "|" + text + '\t\t' + string.ljust(finalValue,step-len(tab.expandtabs())-pad) + "|"
            stdout.write ("|" + '\t\t\t')
            print_dashed_line(step-len(tab.expandtabs())-pad)
        else:
            print "|" + '\t\t\t' + string.ljust(finalValue,step-len(tab.expandtabs())-pad) + "|" 
        count += 1
    print_dashed_line(INFOBOX_LENGTH)

# specific function to print values of Films (ACTORS)
def print_films(topicResult, validEntries, INFOBOX_LENGTH):
    filmText = " Films:" + '\t\t'
    filmSubText1 = "Character" 
    filmSubText2 = "Film Name"
    step = INFOBOX_LENGTH-len(filmText.expandtabs())
    filmValue = topicResult["property"]["/film/actor/film"]["values"]
    filmValue_characters = []
    filmValue_characters.append(filmSubText1)
    filmValue_films = []
    filmValue_films.append(filmSubText2)
    for f in filmValue:
        if "/film/performance/character" in f["property"]:
            if len(f["property"]["/film/performance/character"]["values"]) > 0:
                filmValue_characters.append(f["property"]["/film/performance/character"]["values"][0]["text"])
            else:
                filmValue_characters.append(" ")
        else:
            filmValue_characters.append(" ")
        if "/film/performance/film" in f["property"]:
            if len(f["property"]["/film/performance/film"]["values"]) > 0:
                filmValue_films.append(f["property"]["/film/performance/film"]["values"][0]["text"])
            else:
                filmValue_films.append(" ")
        else:
            filmValue_characters.append(" ")
    count = 0
    tab = '\t'
    for f in filmValue_characters:
        filmFinalValue = "| " + string.ljust(f,step/3)  + "| " + filmValue_films[count] 
        if count == 0:
            print "| Films:" + '\t\t' + string.ljust(filmFinalValue,step-len(tab.expandtabs())) + "|"
            stdout.write ("|" + '\t\t\t')
            print_dashed_line(step-len(tab.expandtabs()))
        else:
            print "|" + '\t\t\t' + string.ljust(filmFinalValue,step-len(tab.expandtabs())) + "|"
        count += 1
    print_dashed_line(INFOBOX_LENGTH)

# specific function to print values of Teams (SPORTS)
def print_teams(topicResult, validEntries, INFOBOX_LENGTH):
    tab = '\t'
    teamsText = " Teams:" + '\t\t'
    teamsValue = topicResult["property"]["/sports/sports_league/teams"]["values"]
    teamsValue_pieces = []
    step = INFOBOX_LENGTH-len(teamsText.expandtabs())
    for t in teamsValue:
        if "/sports/sports_league_participation/team" in t["property"]:
            if len(t["property"]["/sports/sports_league_participation/team"]["values"]) > 0:
                teamsValue_pieces.append(t["property"]["/sports/sports_league_participation/team"]["values"][0]["text"])
            else:
                break
    count = 0
    for t in teamsValue_pieces:
        if count == 0:
            print "|" + teamsText + string.ljust(t,step-len(tab.expandtabs())) + "|"
        else: 
            print "|" + '\t\t\t' + string.ljust(t,step-len(tab.expandtabs())) + "|"
        count += 1
    print_dashed_line(INFOBOX_LENGTH)

# prints dashed line between rows
def print_dashed_line(lineLength):
    for x in range(0,lineLength):
        if x == 0:
            stdout.write(" ")
        else:
            stdout.write("-")
    print ''

# maps Freebase tags to strings describing valid entries
def map_Entries(validEntries):
    entrySet = set()
    for e in validEntries:
        if e == "/people/person":
            entrySet.add("PERSON")
        elif e == "/book/author":
            entrySet.add("AUTHOR")
        elif e == "/film/actor":
            entrySet.add("ACTOR")
        elif e == "/tv/tv_actor":
            entrySet.add("ACTOR")
        elif e == "/organization/organization_founder":
            entrySet.add("BUSINESS")
        elif e == "/business/board_member":
            entrySet.add("BUSINESS")
        elif e == "/sports/sports_league":
            entrySet.add("LEAGUE")
        elif e == "/sports/sports_team":
            entrySet.add("SPORTS TEAM")
        elif e == "/sports/professional_sports_team":
            entrySet.add("SPORTS TEAM")
    return list(entrySet)

def answer_query(query, key):                                   #Main code to answer a question
    def print_sentence(entity_list, sentence, length):          #Helper function to print out entities in sentence format
        if length == 1:                                         #If only one entity, returns that entity
            sentence += str(entity_list[0])
            return sentence
        elif length == 2:                                       #If two entities, returns in form 'X and Y'
            sentence += str(entity_list[0]) + ' and '
            return print_sentence(entity_list[1:], sentence, 1)
        else:                                                   #If more than two entities, returns in form 'X, Y, ... and Z'
            sentence += str(entity_list[0]) + ', '
            return print_sentence(entity_list[1:], sentence, length - 1)
    valid_query = is_valid(query.lower())                               #Calls is_valid to see if query is in valid format
    if valid_query:
        url = 'https://www.googleapis.com/freebase/v1/mqlread?' 
        book_query = '[{ "works_written": [{ "name": null, "name~=": "' + urllib.quote(valid_query) + '" }], "name": null, "type": "/book/author" }]'
        book_url = url + 'query=' + book_query + '&key=' + key
        book_dict = parse_answer(book_url, 'book')              #Calls parse_answer for query of type 'book'
        organization_query = '[{ "organizations_founded": [{ "name": null, "name~=": "' + urllib.quote(valid_query) + '" }], "name": null, "type": "/organization/organization_founder" }]'
        organization_url = url + 'query=' + organization_query + '&key=' + key
        organization_dict = parse_answer(organization_url, 'organization')  #Calls parse_answer for query of type 'organization'
        total_dict = dict(book_dict, **organization_dict) #Combines book_dict and organization_dict
        i = 1                                             #Initializes counter
        for person in sorted(total_dict.keys()):          #Sorts total_dict by name
            print str(i) + '. ' + person + ' created ' + print_sentence(total_dict[person], '', len(total_dict[person]))
            i += 1
    else:
        print "Wrong question!!!"       #Returns error if question is in wrong format

def is_valid(query):                    #Checks if question is in 'Who created X?' format
    matchObj = re.match("who created (.*).* ?", query[:-1])
    if matchObj:
        return matchObj.group(1)        
    else:
        return False

def parse_answer(url, entity_type):     #Parses response object for book_query or organization_query
    answer = json.loads(urllib.urlopen(url).read())
    reply_dict = collections.defaultdict(list)      #Creates dictionary to handle {name:[entities]} pairs
    if entity_type == 'organization':
        for obj in answer["result"]:
            name = obj["name"].encode('ascii', 'replace')
            organizations = obj["organizations_founded"]    #Finds organizations founded by person
            for organization in organizations:              #Adds organizations to dictionary entry for person
                reply_dict[name + ' (as BusinessPerson)'].append('<' + organization["name"].encode('ascii', 'replace') + '>')
    elif entity_type == 'book':
        for obj in answer["result"]:
            name = obj["name"].encode('ascii', 'replace')
            books = obj["works_written"]        #Finds works written by person
            for book in books:                  #Adds books to dictionary entry for person
                reply_dict[name + ' (as Author)'].append('<' + book["name"].encode('ascii', 'replace') + '>')
    return reply_dict

def usage():
    sys.stderr.write("""
    Usage: 
        python knowledge_graph.py -key <Freebase API key> -q <query> -t <infobox|question>
                OR
        python knowledge_graph.py -key <Freebase API key> -f <file of queries> -t <infobox|question>

        Evalute the accuracy of a output trees compared to a key file.\n""")

if __name__ == "__main__": 
    if len(sys.argv) == 7:
        main(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[6])
    else:
        usage()
        sys.exit(1)
