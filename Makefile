all: run
run_query: knowledge_graph.py
	python knowledge_graph.py -key $(APIKEY) -q $(QUERY) -t $(TYPE)
run_file: knowledge_graph.py
	python knowledge_graph.py -key $(APIKEY) -f $(FILE) -t $(TYPE)
