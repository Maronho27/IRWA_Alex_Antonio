import os
from json import JSONEncoder

# pip install httpagentparser
import httpagentparser  # for getting the user agent as json
import nltk
from flask import Flask, render_template, session
from flask import request
import json

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc, SearchedQueries, SearchedTerms, Session, Mission, Ranking, Ranking_2
from myapp.search.algorithms import build_terms, create_index_tf_idf
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document, StatsDocument
from myapp.search.search_engine import SearchEngine


# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

# end lines ***for using method to_json in objects ***

# instantiate the Flask application
app = Flask(__name__)

# random 'secret_key' is used for persisting data in secure cookie
app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
# open browser dev tool to see the cookies
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'

# instantiate our search engine
search_engine = SearchEngine()

# instantiate our in memory persistence
analytics_data = AnalyticsData()

# This will run only once, when the user enters the page
@app.before_first_request
def do_something_only_once():
    """
    Create the corpus containing the tweets and the inverted index, tf, df, idf
    """
    full_path = os.path.realpath(__file__)
    path, filename = os.path.split(full_path)
    file_path = path + "/tw_hurricane_data.json"
    file_path_2 = path + "/tweet_document_ids_map.csv"

    # file_path = "../../tweets-data-who.json"
    global ind, tf, df, idf, corpus, session_, mission

    # load the corpus
    corpus = load_corpus(file_path, file_path_2)

    session_ = []
    mission = []

    # create the inverted index, the tf, the df and the idf
    ind, tf, df, idf = create_index_tf_idf(corpus, len(corpus))

# Home URL "/"
@app.route('/')
def index():
    """
    Create a central search box for users to enter a query and a button to execute the search
    """

    print("starting home url /...")

    # flask server creates a session by persisting a cookie in the user's browser.
    # the 'session' object keeps data between multiple requests
    session['some_var'] = "IRWA 2021 home"

    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent)

    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)

    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))

    print(session)

    return render_template('index.html', page_title="Welcome")


@app.route('/search', methods=['POST'])
def search_form_post():
    """
    Execute the search and show the ordered results. Also pick information for the analytics
    """
    search_query = request.form['search-query']

    # store the query for the analytics
    if search_query in analytics_data.fact_queries.keys():
        analytics_data.fact_queries[search_query] += 1
    else:
        analytics_data.fact_queries[search_query] = 1

    terms = build_terms(search_query)

    # store the terms for the analytics
    for i in terms:
        if i in analytics_data.fact_terms.keys():
            analytics_data.fact_terms[i] += 1
        else:
            analytics_data.fact_terms[i] = 1

    # store the query
    session['last_search_query'] = search_query

    # generate the search id
    search_id = analytics_data.save_query_terms(search_query)

    # obtain the results from the search query
    try:
        results = search_engine.search(search_query, search_id, corpus, ind, tf, df, idf)
    except:
        result = None
        pass

    found_count = len(results)
    session['last_found_count'] = found_count

    # accumulate all the rankings
    for result in results:
        analytics_data.fact_ranking[result.id] = {"query":search_query, "ranking":result.ranking}

    # append the search query to session and save it in the analytics data
    session_.append(search_query)
    analytics_data.fact_sessions[str(1)] = session_

    # check if there is some term that coincides with the previous query and if so consider that this query is part of the current mission
    identifer = 0
    for term in build_terms(analytics_data.last_query):
        if term in search_query:
            identifer = 1

    if identifer == 1:
        mission.append(search_query)

        array = []
        for i in mission:
            array.append(i)

        analytics_data.fact_missions[str(analytics_data.counter)] = array
    else:
        analytics_data.counter += 1
        mission.clear()
        mission.append(search_query)

        array = []
        for i in mission:
            array.append(i)
        analytics_data.fact_missions[str(analytics_data.counter)] = array
    
    # store the query
    analytics_data.last_query = search_query

    print(session)

    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count)


@app.route('/doc_details', methods=['GET'])
def doc_details():
    """
    Show information of the documents selected in the previous section ordered. Also picks some information for the analytics
    """
    # getting request parameters:
    # user = request.args.get('user')

    print("doc details session: ")
    print(session)

    res = session["some_var"]

    print("recovered var from session:", res)

    # get the query string parameters from request
    clicked_doc_id = request.args["id"]
    p1 = int(request.args["search_id"])  # transform to Integer
    p2 = int(request.args["param2"])  # transform to Integer
    doc = corpus[clicked_doc_id]

    # keep only the ranking of the selected document
    try:
        analytics_data.fact_ranking_2[analytics_data.fact_ranking[clicked_doc_id]["query"]+ corpus[clicked_doc_id].title]["value"] += 1
    except:
        analytics_data.fact_ranking[clicked_doc_id]["query"]
        corpus[clicked_doc_id].title
        analytics_data.fact_ranking_2[analytics_data.fact_ranking[clicked_doc_id]["query"]+ corpus[clicked_doc_id].title] = {"query":analytics_data.fact_ranking[clicked_doc_id]["query"], "document":corpus[clicked_doc_id].title, "value":1, "ranking":analytics_data.fact_ranking[clicked_doc_id]["ranking"]}

    # store the number of times that a ranking has been selected
    try:
        analytics_data.fact_ranking_3[analytics_data.fact_ranking[clicked_doc_id]["ranking"]] += 1
    except:
        analytics_data.fact_ranking_3[analytics_data.fact_ranking[clicked_doc_id]["ranking"]] = 1

    print("click in id={}".format(clicked_doc_id))

    # store data of the clicked document
    if clicked_doc_id in analytics_data.fact_clicks.keys():
        analytics_data.fact_clicks[clicked_doc_id] += 1
    else:
        analytics_data.fact_clicks[clicked_doc_id] = 1

    print("fact_clicks count for id={} is {}".format(clicked_doc_id, analytics_data.fact_clicks[clicked_doc_id]))

    return render_template('doc_details.html', doc=doc)


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example
    """

    docs = []
    queries = []
    terms = []
    sessions = []
    missions = []
    rankings = []
    rankings_2 = []

    # Save the documents clicked as an object in docs
    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[doc_id]
        count = analytics_data.fact_clicks[doc_id]
        doc = StatsDocument(row.id, row.title, row.description, row.doc_date, row.url, count)
        docs.append(doc)

    # Save the queries searched as an object in queries
    for query in analytics_data.fact_queries:
        count = analytics_data.fact_queries[query]
        queries.append(SearchedQueries(query, count))

    # Save the terms searched as an object in terms
    for term in analytics_data.fact_terms:
        count = analytics_data.fact_terms[term]
        terms.append(SearchedTerms(term, count))

    # Save the session information as an object in sessions
    for session in analytics_data.fact_sessions:
        count = len(analytics_data.fact_sessions[session])
        sessions.append(Session(1, count, analytics_data.fact_sessions[session]))

    # Save the mission information as an object in missions
    counter = 1
    for mission in analytics_data.fact_missions:
        count = len(analytics_data.fact_missions[mission])
        missions.append(Mission(counter, count, analytics_data.fact_missions[mission]))
        counter += 1

    # Save the ranking of the documents clicked as an object in rankings
    for ranking in analytics_data.fact_ranking_2:
        rankings.append(Ranking(analytics_data.fact_ranking_2[ranking]["document"], analytics_data.fact_ranking_2[ranking]["query"], analytics_data.fact_ranking_2[ranking]["value"], analytics_data.fact_ranking_2[ranking]["ranking"]))

    # Save the ranking of the documents clicked as an object in rankings
    for ranking in analytics_data.fact_ranking_3:
        rankings_2.append(Ranking_2(ranking, analytics_data.fact_ranking_3[ranking]))

    # sort
    docs.sort(key=lambda doc: doc.count, reverse=True)
    queries.sort(key=lambda query: query.value, reverse=True)
    terms.sort(key=lambda term: term.value, reverse=True)
    missions.sort(key=lambda mission: mission.number_queries, reverse=True)
    rankings.sort(key=lambda ranking: ranking.ranking, reverse=True)
    rankings_2.sort(key=lambda ranking: ranking.value, reverse=True)
    return render_template('stats.html', clicks_data=[docs, queries, terms, sessions, missions, rankings, rankings_2])


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Show dashboards of the statistics
    """
    visited_docs = []
    queries = []
    terms = []
    missions = []
    rankings = []

    print(analytics_data.fact_clicks.keys())

    # Save the documents clicked as an object in docs
    for doc_id in analytics_data.fact_clicks.keys():
        d: Document = corpus[doc_id]
        doc = ClickedDoc(doc_id, d.description, analytics_data.fact_clicks[doc_id])
        visited_docs.append(doc)

    visited_docs.sort(key=lambda doc: doc.counter, reverse=True)
    visited_ser=[]
    # save the docs as a json for being able to show the dashboard
    for doc in visited_docs:
        visited_ser.append(doc.to_json())

    # Save the queries searched as an object in queries
    for query in analytics_data.fact_queries:
        count = analytics_data.fact_queries[query]
        queries.append(SearchedQueries(query, count))

    queries.sort(key=lambda query: query.value, reverse=True)
    searched_queries=[]
    # save the queries as a json for being able to show the dashboard
    for query in queries:
        searched_queries.append(query.to_json())

    # Save the terms searched as an object in terms
    for term in analytics_data.fact_terms:
        count = analytics_data.fact_terms[term]
        terms.append(SearchedTerms(term, count))

    terms.sort(key=lambda term: term.value, reverse=True)
    searched_terms=[]
    # save the terms as a json for being able to show the dashboard
    for term in terms:
        searched_terms.append(term.to_json())

    # Save the mission information as an object in missions
    counter = 1
    for mission in analytics_data.fact_missions:
        count = len(analytics_data.fact_missions[mission])
        missions.append(Mission(counter, count, analytics_data.fact_missions[mission]))
        counter += 1

    missions.sort(key=lambda mission: mission.number_queries, reverse=True)
    missions_2=[]
    # save the missions as a json for being able to show the dashboard
    for mission in missions:
        missions_2.append(mission.to_json())

    # Save the ranking of the documents clicked as an object in rankings
    for ranking in analytics_data.fact_ranking_3:
        rankings.append(Ranking_2(ranking, analytics_data.fact_ranking_3[ranking]))

    rankings.sort(key=lambda ranking: ranking.ranking, reverse=True)
    rankings_2=[]
    # save the ranking as a json for being able to show the dashboard
    for ranking in rankings:
        rankings_2.append(ranking.to_json())

    return render_template('dashboard.html', visited_docs=visited_ser, searched_queries=searched_queries, searched_terms=searched_terms, missions_2=missions_2, rankings_2=rankings_2)


@app.route('/sentiment')
def sentiment_form():
    return render_template('sentiment.html')


@app.route('/sentiment', methods=['POST'])
def sentiment_form_post():
    text = request.form['text']
    nltk.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    score = ((sid.polarity_scores(str(text)))['compound'])
    return render_template('sentiment.html', score=score)


if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False)
