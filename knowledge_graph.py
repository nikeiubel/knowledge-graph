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
    def print_sentence(entity_list, sentence, length):
        if length == 1:
            sentence += str(entity_list[0])
            return sentence
        elif length == 2:
            sentence += str(entity_list[0]) + ' and '
            return print_sentence(entity_list[1:], sentence, 1)
        else:
            sentence += str(entity_list[0]) + ', '
            return print_sentence(entity_list[1:], sentence, length - 1)
    valid_query = is_valid(query)
    if valid_query:
        url = 'https://www.googleapis.com/freebase/v1/mqlread?'
        book_query = '[{ "works_written": [{ "name": null, "name~=": "' + urllib.quote(valid_query) + '" }], "name": null, "type": "/book/author" }]'
        book_url = url + 'query=' + book_query + '&key=' + key
        book_dict = parse_answer(book_url, 'book')
        organization_query = '[{ "organizations_founded": [{ "name": null, "name~=": "' + urllib.quote(valid_query) + '" }], "name": null, "type": "/organization/organization_founder" }]'
        organization_url = url + 'query=' + organization_query + '&key=' + key
        organization_dict = parse_answer(organization_url, 'organization')
        total_dict = dict(book_dict, **organization_dict)
        i = 1
        for person in sorted(total_dict.keys()):
            print str(i) + '. ' + person + ' created ' + print_sentence(total_dict[person], '', len(total_dict[person]))
            i += 1
    else:
        print "Wrong question!!!"

def is_valid(query):
    matchObj = re.match("Who created (.*).* ?", query[:-1])
    if matchObj:
        return matchObj.group(1)
    else:
        return False

def parse_answer(url, entity_type):
    answer = json.loads(urllib.urlopen(url).read())
    reply_dict = collections.defaultdict(list)
    if entity_type == 'organization':
        for obj in answer["result"]:
            name = obj["name"].encode('ascii', 'replace')
            organizations = obj["organizations_founded"]
            for organization in organizations:
                reply_dict[name + ' (as BusinessPerson)'].append('<' + organization["name"].encode('ascii', 'replace') + '>')
    elif entity_type == 'book':
        for obj in answer["result"]:
            name = obj["name"].encode('ascii', 'replace')
            books = obj["works_written"]
            for book in books:
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
