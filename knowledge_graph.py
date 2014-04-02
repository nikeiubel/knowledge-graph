import sys, string, urllib, urllib2

#Freebase API key = AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs
#Example usage: https://www.googleapis.com/freebase/v1/search?query=bob&key=AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs

def main(key, option, query, response):
    if option == '-q':
        return query_freebase(query,key)
    elif option == '-f':
        pass

def query_freebase(query, key):
    q = {'query':query, 'key':key}
    url = 'https://www.googleapis.com/freebase/v1/search?' + urllib.urlencode(q)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    content = response.read()
    print content

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
