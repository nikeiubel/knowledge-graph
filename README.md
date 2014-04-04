a) Your name and your partner's name and Columbia UNI
Nikolas Iubel, nfi2103
Elaine Mao, ekm2133

b) A list of all the files that you are submitting
knowledge_graph.py
README.md
Makefile
<name of transcript file>

c) A clear description of how to run your program (note that your project must compile/run under Linux in your CS account)
Our program can be run in either of the two ways specified in the assignment: 
$ python knowledge_graph.py -key <Freebase API key> -q <query> -t <infobox|question>
                OR
$ python knowledge_graph.py -key <Freebase API key> -f <file of queries> -t <infobox|question>
We did not implement the optional interactive mode.

d) A clear description of the internal design of your project, including listing the mapping that you used to map from Freebase properties to the entity properties of interest that you return
When the program is run as specified above in part (c), the key, -q/f option, the name of the query or file, and the infobox/question option are passed to the "main" function. Then, depending on whether the option is -q or -f, the main function either passes the query to the next function directly, or it opens the query file and passes each line as an argument to the next function. If the user requests an infobox, the main function passes the key and the query to query_freebase_search. If the user requests the answer to a question, the main function passes the key and the query to answer_query. Any other option will call the usage function, which tells the user how to call the program correctly.

The query_freebase_search function queries the Freebase Search API and receives a JSON document in return. It then extracts the mid values from the results and calls query_freebase_topic, which queries the Freebase Topic API to see if the entity is of one of the six high-level types specified in the assignment. 
#WRITE MORE HERE LATER

The answer_query function first checks to see if the query is in a valid format, e.g. "Who created X?" by passign the query to the is_valid function. If the query is valid, answer_query generates two separate queries to the MQL Read API--one finds the names of authors who wrote books with the query in the title, the other finds the names of businesspeople who founded companies with the query in the title. After calling parse_answer to extract the relevant information from the result, answer_query then combines all the results into a dictionary and sorts the dictionary by key (name), and then finally outputs the result in the format specified in the assignment and the reference implementation. 

Please see below for the mapping from Freebase properties to entity properties of interest:

#FINISH THIS LATER


f) Your Freebase API Key (so we can test your project) as well as the requests per second per user that you have set when you configured your Google project (see Freebase Basics section)
Freebase API Key: AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs
10.0 requests/second/user

g) Any additional information that you consider significant
No additional information.
