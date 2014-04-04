import json, sys, string, urllib, urllib2, re, collections

#Freebase API key = AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs
#Example usage: https://www.googleapis.com/freebase/v1/search?query=bob&key=AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs

def main(key, option, query, response):
    if option == '-q':
        if response == 'infobox':
            query_freebase_search(query,key)
        elif response == 'question':
            answer_query(query,key)
        else:
            usage()
    elif option == '-f':
        f = open(query, 'r')
        if response == 'infobox':
            for line in f:
                print "\n" + line
                query_freebase_search(line,key)
        elif response == 'question':
            for line in f:
                print "\n" + line
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
    for obj in content["result"]:
        if (query_freebase_topic(key, obj["mid"])):   # will stop at the top-level mid containing valid entry
            break     
    print validEntries

def query_freebase_topic(key, mid):
    url = 'https://www.googleapis.com/freebase/v1/topic'
    params = {
        'key': key,
        'filter': 'suggest'
    }
    url += mid + '?' + urllib.urlencode(params)
    topic = json.loads(urllib.urlopen(url).read())
    for entry in topic["property"]["/type/object/type"]["values"]:
        entries.append(str(entry["id"]))
    validEntities = {"/people/person","/book/author","/film/actor","/tv/tv_actor","/organization/organization_founder","/business/board_member","/sports/sports_league","/sports/sports_team","/sports/professional_sports_team"}
    if any(entry in validEntities for entry in entries):
        for e in entries:
            if e in validEntities:
                validEntries.append(e)
        return True
    else:
        del entries[:]
        return False  

def answer_query(query, key):
    valid_query = is_valid(query)
    if valid_query:
        url = 'https://www.googleapis.com/freebase/v1/mqlread?'
        entity_type = get_type(valid_query,key)
        if entity_type == '/book/book':
            book_query = '[{ "works_written": [{ "name": null, "name~=": "' + urllib.quote(valid_query) + '" }], "name": null, "type": "/book/author" }]'
            book_url = url + 'query=' + book_query + '&key=' + key
            parse_answer(book_url, 'book')
        elif entity_type == '/organization/organization':
            organization_query = '[{ "organizations_founded": [{ "name": null, "name~=": "' + urllib.quote(valid_query) + '" }], "name": null, "type": "/organization/organization_founder" }]'
            organization_url = url + 'query=' + organization_query + '&key=' + key
            parse_answer(organization_url, 'organization')
        else:
            print valid_query + " is not a book or an organization."
    else:
        print "That is not a valid query."

def is_valid(query):
    matchObj = re.match("Who created (.*).* ?", query[:-1])
    if matchObj:
        return matchObj.group(1)
    else:
        return False

def get_type(query,key):
    q = {'query':query, 'key':key}
    url = 'https://www.googleapis.com/freebase/v1/search?' + urllib.urlencode(q)
    req = urllib2.Request(url)
    content = json.loads(urllib2.urlopen(req).read())
    global results
    results = []
    for obj in content["result"]:
        result_type = top_freebase_topic(key, obj["mid"])
        if result_type:   # will stop at the top-level mid containing valid entry
            return result_type
    return False 

def top_freebase_topic(key, mid):
    url = 'https://www.googleapis.com/freebase/v1/topic'
    params = {
        'key': key,
        'filter': 'suggest'
    }
    url += mid + '?' + urllib.urlencode(params)
    topic = json.loads(urllib.urlopen(url).read())
    for result in topic["property"]["/type/object/type"]["values"]:
        results.append(str(result["id"]))
    validEntities = {"/book/book","/organization/organization"}
    if any(result in validEntities for result in results):
        for r in results:
            if r in validEntities:
                return r
    else:
        del results[:]
        return None 

def parse_answer(url, entity_type):
    answer = json.loads(urllib.urlopen(url).read())
    reply_dict = collections.defaultdict(list)
    def print_sentence(entity_list, sentence, length):
        if length == 1:
            sentence += str(entity_list[0])
            return sentence
        elif length == 2:
            sentence += str(entity_list[0]) + ', and '
            return print_sentence(entity_list[1:], sentence, 1)
        else:
            sentence += str(entity_list[0]) + ', '
            return print_sentence(entity_list[1:], sentence, length - 1)
    if entity_type == 'organization':
        for obj in answer["result"]:
            name = obj["name"]
            organizations = obj["organizations_founded"]
            for organization in organizations:
                reply_dict[name].append(organization["name"])
        for person in sorted(reply_dict.keys()):
            print person + ' (as BusinessPerson) created ' + print_sentence(reply_dict[person], '', len(reply_dict[person])) + '.'
    elif entity_type == 'book':
        for obj in answer["result"]:
            name = obj["name"]
            books = obj["works_written"]
            for book in books:
                reply_dict[name].append(book["name"])
        for person in sorted(reply_dict.keys()):
            print person + ' (as Author) created ' + print_sentence(reply_dict[person], '', len(reply_dict[person])) + '.'

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
    elif len(sys.argv) == 3:
        interactive(sys.argv[2])
    else:
        usage()
        sys.exit(1)
