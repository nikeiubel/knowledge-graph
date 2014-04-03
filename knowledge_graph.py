import json, sys, string, urllib, urllib2

#Freebase API key = AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs
#Example usage: https://www.googleapis.com/freebase/v1/search?query=bob&key=AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs

def main(key, option, query, response):
    if option == '-q':
        return query_freebase_search(query,key)
    elif option == '-f':
        pass

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
