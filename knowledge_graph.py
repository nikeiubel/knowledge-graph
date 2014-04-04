import json, sys, string, urllib, urllib2, re, collections
from sys import stdout

#Freebase API key = AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs
#Example usage: https://www.googleapis.com/freebase/v1/search?query=bob&key=AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs

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
    req = urllib2.Request(url)   # why do we need this? not used in API sample code
    content = json.loads(urllib2.urlopen(req).read())
    global entries
    global validEntries
    entries = []
    validEntries = []
    topicResult = dict()
    for obj in content["result"]:
        topicResult = query_freebase_topic(key, obj["mid"])
        if (topicResult):
        #if (query_freebase_topic(key, obj["mid"])):   # will stop at the top-level mid containing valid entry
            break    
    #print validEntries
    output_infobox(topicResult, validEntries)

def query_freebase_topic(key, mid):
    url = 'https://www.googleapis.com/freebase/v1/topic'
    params = {
        'key': key,
       # 'filter': 'suggest'
    }
    url += mid + '?' + urllib.urlencode(params)
    topic = json.loads(urllib.urlopen(url).read())
    #print urllib.urlopen(url).read()
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

def output_infobox (topicResult, validEntries):
    INFOBOX_LENGTH = 98
    name = topicResult["property"]["/type/object/name"]["values"][0]["value"] #get name of topic
    mappedEntries = map_Entries(validEntries)
    #print mappedEntries

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
        bdayText = " Birthday:" + '\t\t' 
        bdayValue = topicResult["property"]["/people/person/date_of_birth"]["values"][0]["value"]
        print "|" + bdayText + string.ljust(bdayValue,INFOBOX_LENGTH-len(bdayText.expandtabs())) + "|"
        print_dashed_line(INFOBOX_LENGTH)

        bplaceText = " Place of Birth:" + '\t'
        bplaceValue = topicResult["property"]["/people/person/place_of_birth"]["values"][0]["text"]
        print "|" + bplaceText + string.ljust(bplaceValue,INFOBOX_LENGTH-len(bplaceText.expandtabs())) + "|"
        print_dashed_line(INFOBOX_LENGTH)

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

        siblingsText = " Siblings:" + '\t\t'
        siblingsValue = topicResult["property"]["/people/person/sibling_s"]["values"]
        siblingsValue_pieces = []
        step = INFOBOX_LENGTH-len(siblingsText.expandtabs())
        for d in siblingsValue:
            siblingsValue_pieces.append(d["property"]["/people/sibling_relationship/sibling"]["values"][0]["text"])
        count = 0
        for d in siblingsValue_pieces:
            if count == 0:
                print "|" + siblingsText + string.ljust(d,step) + "|"
            else: 
                print "|" + '\t\t\t' + string.ljust(d,step) + "|"
            count += 1
        print_dashed_line(INFOBOX_LENGTH)

        spousesText = " Spouses:" + '\t\t'
        spousesValue = topicResult["property"]["/people/person/spouse_s"]["values"]
        spousesValue_spouses = []
        spousesValue_froms = []
        spousesValue_tos = []
        spousesValue_locations = []
        step = INFOBOX_LENGTH-len(spousesText.expandtabs())
        for d in spousesValue:
            if len(d["property"]["/people/marriage/spouse"]["values"]) > 0:
                spousesValue_spouses.append(d["property"]["/people/marriage/spouse"]["values"][0]["text"])
            else:
                break
            if len(d["property"]["/people/marriage/from"]["values"]):
                spousesValue_froms.append(d["property"]["/people/marriage/from"]["values"][0]["text"])
            if len(d["property"]["/people/marriage/to"]["values"]) > 0:
                spousesValue_tos.append(d["property"]["/people/marriage/to"]["values"][0]["text"])
            else:
                spousesValue_tos.append("now")
            if len(d["property"]["/people/marriage/location_of_ceremony"]["values"]) > 0:
                spousesValue_locations.append(d["property"]["/people/marriage/location_of_ceremony"]["values"][0]["text"])
        count = 0
        for d in spousesValue_spouses:
            spouseFinalValue = d + " (" + spousesValue_froms[count] + " - " + spousesValue_tos[count] + ") @ " + spousesValue_locations[count]
            if count == 0:
                print "|" + spousesText + string.ljust(spouseFinalValue,step) + "|"
            else: 
                print "|" + '\t\t\t' + string.ljust(spouseFinalValue,step) + "|"
            count += 1
        print_dashed_line(INFOBOX_LENGTH)

    if "AUTHOR" in mappedEntries:
        bookText = " Books:" + '\t\t'
        bookValue = topicResult["property"]["/book/author/works_written"]["values"]
        step = INFOBOX_LENGTH-len(bookText.expandtabs())
        bookValue_pieces = []
        for b in bookValue:
            bookValue_pieces.append(b["text"])
        count = 0
        for b in bookValue_pieces:
            if count == 0:
                print "|" + bookText + string.ljust(b,step)[:step] + "|"
            else:
                print "|" + '\t\t\t' + string.ljust(b,step)[:step] + "|"
            count += 1
        print_dashed_line(INFOBOX_LENGTH)

        aboutText = " Books about:" + '\t\t'
        aboutValue = topicResult["property"]["/book/book_subject/works"]["values"]
        step = INFOBOX_LENGTH-len(aboutText.expandtabs())
        aboutValue_pieces = []
        for a in aboutValue:
            aboutValue_pieces.append(a["text"])
        count = 0
        for a in aboutValue_pieces:
            if count == 0:
                print "|" + aboutText + string.ljust(a,step)[:step] + "|"
            else:
                print "|" + '\t\t\t' + string.ljust(a,step)[:step] + "|"
            count += 1
        print_dashed_line(INFOBOX_LENGTH)

        influenceText = " Influenced:" + '\t\t'
        influenceValue = topicResult["property"]["/influence/influence_node/influenced"]["values"]
        step = INFOBOX_LENGTH-len(influenceText.expandtabs())
        influenceValue_pieces = []
        for i in influenceValue:
            influenceValue_pieces.append(i["text"])
        count = 0
        for i in influenceValue_pieces:
            if count == 0:
                print "|" + influenceText + string.ljust(i,step)[:step] + "|"
            else:
                print "|" + '\t\t\t' + string.ljust(i,step)[:step] + "|"
            count += 1
        print_dashed_line(INFOBOX_LENGTH)

    if "BUSINESS" in mappedEntries:
        foundedText = " Founded:" + '\t\t'
        foundedValue = topicResult["property"]["/organization/organization_founder/organizations_founded"]["values"]
        step = INFOBOX_LENGTH-len(foundedText.expandtabs())
        foundedValue_pieces = []
        for f in foundedValue:
            foundedValue_pieces.append(f["text"])
        count = 0
        for f in foundedValue_pieces:
            if count == 0:
                print "|" + foundedText + string.ljust(f,step)[:step] + "|"
            else:
                print "|" + '\t\t\t' + string.ljust(f,step)[:step] + "|"
            count += 1
        print_dashed_line(INFOBOX_LENGTH)

def print_dashed_line(lineLength):
    for x in range(0,lineLength):
        if x == 0:
            stdout.write(" ")
        else:
            stdout.write("-")
    print ''

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
            entrySet.add("SPORTSTEAM")
        elif e == "/sports/professional_sports_team":
            entrySet.add("SPORTSTEAM")
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
                OR
        python knowledge_graph.py -key <Freebase API key>

        Evalute the accuracy of a output trees compared to a key file.\n""")

if __name__ == "__main__": 
    if len(sys.argv) == 7:
        main(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[6])
    else:
        usage()
        sys.exit(1)
