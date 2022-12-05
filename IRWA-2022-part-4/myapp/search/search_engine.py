import random

from myapp.search.objects import ResultItem, Document
from myapp.search.algorithms import search_in_corpus


def build_demo_results(corpus, results, search_id):
    """
    Method used for sorting our results

    Arguments:
    corpus: DataFrame with a Document Object representing each tweet
    results: Order of each tweet
    search_id: Id of the searching

    Returns:
    res: Array with a Document Object for each tweet containing at least one of the words of the query sorted by their ranking
    """

    res = []

    # combines the order of results with the information of corpus for returning the corpus correctly sorted
    for index, item in enumerate(results):
        # DF columns: 'Id' 'Tweet' 'Username' 'Date' 'Hashtags' 'Likes' 'Retweets' 'Url' 'Language'
        res.append(ResultItem(corpus[item].id, corpus[item].title, corpus[item].description, corpus[item].doc_date,
                                 "doc_details?id={}&search_id={}&param2=2".format(corpus[item].id, search_id), index + 1))

    return res


class SearchEngine:
    """educational search engine"""

    def search(self, search_query, search_id, corpus, index, tf, df, idf):
        """
        Combine search_in_corpus() and build_demo_results() for finding and ordering the documents containing at least one of the words
        of the query

        Arguments:
        search_query: query searched by the user
        search_id: id of the search
        corpus: DataFrame containing all the tweets in the Document object format
        index: Inverted Index
        tf: Term Frequency
        df: document frequency
        idf: inverted document frequency

        Returns:
        results: Array with a Document Object for each tweet containing at least one of the words of the query sorted by their ranking
        """

        results = []
        results = search_in_corpus(search_query, index, tf, df, idf)

        results = build_demo_results(corpus, results, search_id)  # replace with call to search algorithm

        return results
