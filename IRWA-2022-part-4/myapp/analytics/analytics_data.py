import json
import random


class AnalyticsData:
    """
    An in memory persistence object.
    Declare more variables to hold analytics tables.
    """
    # statistics table 1
    # fact_clicks is a dictionary with the click counters: key = doc id | value = click counter
    fact_clicks = dict([])

    # dictionary where we will store the session information
    fact_sessions = dict([])

    # dictionary where we will store the missions information
    fact_missions = dict([])

    # dictionary where we will store the queries information
    fact_queries = dict([])

    # dictionary where we will store the terms used in the queries information
    fact_terms = dict([])

    # dictionary where we will store the ranking of all the documents
    fact_ranking = dict([])

    # dictionary where we will store the ranking of the document selected
    fact_ranking_2 = dict([])

    # dictionary where we will store the number of times that a ranking has been selected
    fact_ranking_3 = dict([])

    # counter for stablishing an id for the missions
    counter = 0

    # last query searched (used for identifying if it is a new mission or not)
    last_query = ""

    def save_query_terms(self, terms: str) -> int:
        """
        Returns a random number as search query id

        Arguments:
        terms: search query

        Returns:
        random.randint(0, 100000): search id
        """
        print(self)
        return random.randint(0, 100000)

# create the class for storing the clicked documents
class ClickedDoc:
    def __init__(self, doc_id, description, counter):
        self.doc_id = doc_id
        self.description = description
        self.counter = counter

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)

# create the class for storing the searched queries
class SearchedQueries:
    def __init__(self, query, value):
        self.query = query
        self.value = value

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)

# create the class for storing the searched terms
class SearchedTerms:
    def __init__(self, term, value):
        self.term = term
        self.value = value

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)

# create the class for storing the session
class Session:
    def __init__(self, session_id, number_queries, queries):
        self.session_id = session_id
        self.number_queries = number_queries
        self.queries = queries

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)

# create the class for storing the mission
class Mission:
    def __init__(self, mission_id, number_queries, queries):
        self.mission_id = mission_id
        self.number_queries = number_queries
        self.queries = queries

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)

# create the class for storing the ranking
class Ranking:
    def __init__(self, document, query, value, ranking):
        self.document = document
        self.query = query
        self.value = value
        self.ranking = ranking

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)

# create the class for storing the number of times that a rank has been selected
class Ranking_2:
    def __init__(self, ranking, value):
        self.ranking = ranking
        self.value = value

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)
