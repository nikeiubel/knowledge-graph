a) Your name and your partner's name and Columbia UNI
Nikolas Iubel, nfi2103
Elaine Mao, ekm2133

b) A list of all the files that you are submitting
knowledge_graph.py
README.md
Makefile
Transcript.txt

c) A clear description of how to run your program (note that your project must compile/run under Linux in your CS account)
Our program can be run in either of the two ways specified in the assignment: 

 Run the program as follows: 

1) Terminal:
$ python knowledge_graph.py -key <Freebase API key> -q <query> -t <infobox|question>
                OR
$ python knowledge_graph.py -key <Freebase API key> -f <file of queries> -t <infobox|question>
TA Ayushi Singhal wrote on Piazza that implementing the interactive mode was optional, so we did not implement it.

Examples:
python knowledge_graph.py -key AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs -q 'Bill Gates' -t infobox
python knowledge_graph.py -key AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs -q 'Who created Romeo and Juliet?' -t question

 2) Makefile: Run program with Makefile in the following manner:

    make PRECISION=[precision@10] QUERY=[query]
    make APIKEY=[api_key] QUERY=[query] TYPE=['infobox'/'question']

 Examples:
 make APIKEY='AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs' QUERY="\"Bill Gates"\" TYPE='infobox' (make sure to escape the quotation marks)

 In order to run option 2, edit makefile. Replace the flag '-q' with '-f'

 make APIKEY='AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs' QUERY="\"Who created Google?"\" TYPE='question' 

d) A clear description of the internal design of your project, including listing the mapping that you used to map from Freebase properties to the entity properties of interest that you return
When the program is run as specified above in part (c), the key, -q/f option, the name of the query or file, and the infobox/question option are passed to the "main" function. Then, depending on whether the option is -q or -f, the main function either passes the query to the next function directly, or it opens the query file and passes each line as an argument to the next function. If the user requests an infobox, the main function passes the key and the query to query_freebase_search. If the user requests the answer to a question, the main function passes the key and the query to answer_query. Any other option will call the usage function, which tells the user how to call the program correctly.

The query_freebase_search function queries the Freebase Search API and receives a JSON document in return. It then extracts the mid values from the results and calls query_freebase_topic, which queries the Freebase Topic API to see if the entity is of one of the six high-level types specified in the assignment. If a relevant result was returned, function output_infobox prints it out. 

The functions print_list, print_twoLevelsDown and print_bizList are generic functions used to print contents of Freebase entities. Functions print_death, print_description, print_films, print_spouses are specific functions used to print content of specific entities. The mapping from Freebase properties to entity properties of interest is detailed later in this text.

The answer_query function first checks to see if the query is in a valid format, e.g. "Who created X?" by passign the query to the is_valid function. If the query is valid, answer_query generates two separate queries to the MQL Read API--one finds the names of authors who wrote books with the query in the title, the other finds the names of businesspeople who founded companies with the query in the title. After calling parse_answer to extract the relevant information from the result, answer_query then combines all the results into a dictionary and sorts the dictionary by key (name), and then finally outputs the result in the format specified in the assignment and the reference implementation. 

Please see below for the mapping from Freebase properties to entity properties of interest.

The following mappings are done through the print_list function, which extracts the relevant content from tags listed below by following path: "property" -> tag -> "values" -> "text". The function print_list is generic enough to work for entries with one or more values.
- Birthday (PERSON) is mapped to "/people/person/date_of_birth"
- Place of Birth (PERSON) is mapped to "/people/person/date_of_birth"
- Books (AUTHOR) is mapped to "/book/author/works_written"
- Influenced By (AUTHOR) is mapped to "/influence/influence_node/influenced_by"
- Books about (AUTHOR) is mapped to "/book/book_subject/works"
- Influenced (AUTHOR) is mapped to "/influence/influence_node/influenced"
- Founded (BUSINESS) is mapped to "/organization/organization_founder/organizations_founded"
- Sport (LEAGUE) is mapped to "/sports/sports_league/sport"
- Slogan (LEAGUE) is mapped to "/organization/organization/slogan"
- Official Website (LEAGUE) is mapped to "/common/topic/official_website"
- Championship (LEAGUE) is mapped to "/sports/sports_league/championship"
- Sport (SPORTS TEAM) is mapped to "/sports/sports_team/sport"
- Championships (SPORTS TEAM) is mapped to "/sports/sports_team/championships"
- Founded (SPORTS TEAM) is mapped to "/sports/sports_team/founded"
- Locations (SPORTS TEAM) is mapped to "/sports/sports_team/location"

The following mappings are done through the print_twoLevelsDown function, which extracts the relevant content from tags listed below by following path: "property" -> main tag -> "values" -> "property" -> sub tag -> "values" -> "text"
- Siblings (PERSON) is mapped to main tag: "/people/person/sibling_s", sub tag: "/people/sibling_relationship/sibling"
- Arena (SPORTS TEAM) is mapped to main tag: "/sports/sports_team/venue", sub tag: "/sports/team_venue_relationship/venue"
- Leagues (SPORTS TEAM) is mapped to main tag: "/sports/sports_team/league", sub tag: "/sports/sports_league_participation/league"

The following mappings are done the print_listBiz function, which extracts relevant content from multiple subtags under the same parent tag by following path: "property" -> main tag -> "values" -> "property" -> sub tag -> "values" -> "text". Values extracted from multiple subtags are concatenated:
- Leadership (BUSINESS) is mapped to main tag: "/business/board_member/leader_of", sub tags: "/organization/leadership/organization", "/organization/leadership/role", "/organization/leadership/title", "/organization/leadership/from", "/organization/leadership/to"
- Board member (BUSINESS) is mapped to main tag: "/business/board_member/organization_board_memberships", sub tags: 
"/organization/organization_board_membership/organization", "/organization/organization_board_membership/role", 
"/organization/organization_board_membership/title", "/organization/organization_board_membership/from", "/organization/organization_board_membership/to"
- Coaches (SPORTS TEAM) is mapped to main tag: "/sports/sports_team/coaches", sub tags: "/sports/sports_team_coach_tenure/coach", "/sports/sports_team_coach_tenure/position", "/sports/sports_team_coach_tenure/from", "/sports/sports_team_coach_tenure/to"
- Roster (SPORTS TEAM) is mapped to main tag: "/sports/sports_team/roster", sub tags: "/sports/sports_team_roster/player", 
"/sports/sports_team_roster/position", "/sports/sports_team_roster/number", "/sports/sports_team_roster/from", "/sports/sports_team_roster/to"

Some mappings require specific functions:
- Function print_death maps Death (PERSON) to main tag "/people/deceased_person/date_of_death", sub tags: "/people/deceased_person/date_of_death", "/people/deceased_person/place_of_death", "/people/deceased_person/cause_of_death". Mapping follows path: "property" -> main tag -> "values" -> "property" -> sub tag -> "values" -> "text". Values extracted from multiple subtags are concatenated.
- Function print_description maps Description(PERSON, LEAGUE, SPORTS TEAM) to tag "/common/topic/description". Mapping follows path "property" -> tag -> "values" -> "text".
- Function print_spouses maps Spouses (PERSON) to main tag "/people/person/spouse_s", sub tags: "/people/marriage/spouse", "/people/marriage/from", "/people/marriage/to", "/people/marriage/location_of_ceremony". Mapping follows path: "property" -> main tag -> "values" -> "property" -> sub tag -> "values" -> "text". Values extracted from multiple subtags are concatenated.
- Function print_films maps Films (ACTOR) to main tag "/film/actor/film", sub tags: "/film/performance/character", "/film/performance/film". Mapping follows path: "property" -> main tag -> "values" -> "property" -> sub tag -> "values" -> "text". Values extracted from multiple subtags are concatenated.
- Function print_spouses maps Teams (LEAGUE) to main tag "/sports/sports_league/teams", sub tag: "/sports/sports_league_participation/team". Mapping follows path: "property" -> main tag -> "values" -> "property" -> sub tag -> "values" -> "text".

These are the MQL queries for Part 2. The first one finds book authors who have written works whose titles contain <QUERY>, and the second one finds organization founders who have founded organizations whose names contain <QUERY>.

[{ "works_written": [{ "name": null, "name~=": "<QUERY>" }], "name": null, "type": "/book/author" }]

[{ "organizations_founded": [{ "name": null, "name~=": "<QUERY>" }], "name": null, "type": "/organization/organization_founder" }]

From the first query's result, we extracted the ["name"] and ["works_written"] fields.
From the second query's result, we extracted the ["name"] and ["organizations_founded"] fields. 

f) Your Freebase API Key (so we can test your project) as well as the requests per second per user that you have set when you configured your Google project (see Freebase Basics section)
Freebase API Key: AIzaSyCnxmwlxKWsLnzs9d98rcwDhh68kuwHVXs
10.0 requests/second/user

g) Any additional information that you consider significant
Note that the size of the table can be adjusted by altering value of variable INFOBOX_LENGTH.
