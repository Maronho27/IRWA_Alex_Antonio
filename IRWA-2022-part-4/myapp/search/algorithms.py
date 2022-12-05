from collections import defaultdict
from array import array
from nltk.stem import PorterStemmer
#from nltk.corpus import stopwords
import math
import numpy as np
import collections
from numpy import linalg as la
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

def build_terms(tweet):
    """
    Preprocess the text of the tweet by eliminating the url, the people labelled with the @,
    eliminating the punctuation, separating the words after the hashtag, removing stop words, 
    stemming, transforming in lowercase and returning the tokens of the text.
    
    Argument:
    tweet -- string (text) to be pre-processed
    
    Returns:
    tweet - a list of tokens corresponding to the input text after the pre-processing
    """
    stemmer = PorterStemmer() # stemm the words to get the root of the word and avoid having different words that mean the same
    stop_words = set(stopwords.words("english")) # eliminate all the stop words to make efficient queries and documents
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+') # separate the words without including puntuation marks
    
    tweet = re.sub(r'http\S+', '', tweet) ## delete the url
    tweet = re.sub(r'@\S+', '', tweet) ## delete the word after @ (so the people labelled)
    tweet = " ".join([a for a in re.split('([A-Z][a-z]+)', tweet) if a]) ## separate the hashtags in words according to the capital letters
    tweet = tweet.replace("_", " ") ## eliminate the _ (it is the only punctuation mark that is not deleted with tokenize)
    tweet = tweet.lower() ## transform in lowercase
    tweet = tokenizer.tokenize(tweet) ## tokenize the text to get a list of terms and remove punctuation marks
    tweet=[i for i in tweet if i not in stop_words]  ## eliminate the stopwords
    tweet=[stemmer.stem(i) for i in tweet] ## perform stemming

    return tweet

def create_index_tf_idf(tweets, num_tweets):
  """
  Create the inverted index, the tweets dictionary and compute the tf, df and idf

  Argument:
  tweets -- collection of tweets
  num_tweets -- total number of tweets
  
  Returns:
  index -- the inverted index. Contains the terms as keys and in which tweets (appear as the document number related to the tweet id)
  and in which position inside this tweet appears each term
  tf -- normalized term frequency for each term in each tweet
  df -- number of document each term appear in
  idf -- inverse document frequency of each term
  """
  index = defaultdict(list) # Create the inverted index
  tf = defaultdict(list)  # Create the term frequency dictionary
  df = defaultdict(int)  # Create the tweet frequency dictionary
  idf = defaultdict(float) # Create the inverse tweet frequency dictionary
  
  for i in tweets:
    terms = build_terms(tweets[i].title) # call build terms for processing the text of the tweet

    current_page_index = {}

    for position, term in enumerate(terms): # loop over all terms
        try:
            # if the term is already in the index for the current page append the position
            current_page_index[term][1].append(position)
        except:
            # else add the new term as dict key and set the document number corresponding to this tweet and the position where the term appears in this tweet
            current_page_index[term]=[tweets[i].id, array('I',[position])] #'I' indicates unsigned int (int in Python)

    # calculate the denominator to normalize term frequencies for not letting the size of the document matters the ranking
    norm = 0
    for term, posting in current_page_index.items():
        norm += len(posting[1]) ** 2
    norm = math.sqrt(norm)

    # compute the tf (so the frequency of a term in the document) and the df (number of documents containing a certain term)
    for term, posting in current_page_index.items():
        tf[term].append(np.round(len(posting[1])/norm,4))
        df[term] += 1
    
    # compute the idf (for giving more importance to the terms that appear in less documents)
    for term in df:
        idf[term] = np.round(np.log(float(num_tweets/df[term])), 4)

    # merge the current page index with the main index
    for term_page, posting_page in current_page_index.items():
        index[term_page].append(posting_page)

  return index, tf, df, idf

def rank_documents(terms, docs, index, idf, tf, df):
    """
    Rank the results of a query based on the tf-idf weights that we have previously calculated
    
    Argument:
    terms -- list of terms
    docs -- list of tweets to rank matching the query
    index -- inverted index
    idf -- inverted document frequencies
    tf -- term frequencies
    df -- document frequencies
    
    Returns:
    result_docs -- list in order of ranked documents
    """

    # We are only interested on the elements of the docVector corresponding to the query term, due to this, the others will become 0 once that they are multiplied by the query_vector
    doc_vectors = defaultdict(lambda: [0] * len(terms)) # I call doc_vectors[k] for a nonexistent key k, the key-value pair (k,[0]*len(terms)) will be automatically added to the dictionary
    query_vector = [0] * len(terms)

    query_terms_count = collections.Counter(terms)  # get the frequency of each term in the query. 

    query_norm = la.norm(list(query_terms_count.values())) # compute the norm for the query tf

    for termIndex, term in enumerate(terms):  #termIndex is the index of the term in the query
        if term not in index:
            continue

        ## Compute tf*idf
        query_vector[termIndex]=query_terms_count[term]/query_norm * idf[term]

        # Generate doc_vectors for matching docs
        for doc_index, (doc, postings) in enumerate(index[term]):      
            if doc in docs: 
                doc_vectors[doc][termIndex] = tf[term][doc_index] * idf[term]

    # Calculate the score of each doc 
    doc_scores=[[np.dot(curDocVec, query_vector), doc] for doc, curDocVec in doc_vectors.items() ]
    doc_scores.sort(reverse=True) # sort the doc_scores
    
    result_docs = [x[1] for x in doc_scores]

    #print ('\n'.join(result_docs), '\n')
    return result_docs

def search_tf_idf(query, index, tf, df, idf):
    """
    Obtain the list of ranked documents based on the query
    
    Argument:
    query -- list of terms that we want to search
    index -- inverted index
    tf -- term frequencies
    df -- document frequencies
    idf -- inverted document frequencies
    
    Returns:
    ranked_docs -- list in order of ranked documents
    """
    query = build_terms(query) # normalize the query
    docs = set() # create an empty set where we will store the ordered docs for each word in the query
    counter = 0 # create a counter for distinguishing between the first term and the rest of them
    for term in query:
        try:
            # store in term_docs the ids of the docs that contain the current term                    
            term_docs=[posting[0] for posting in index[term]]
            
            # keep the documents that have all terms of the query
            if counter == 0:
              # we have to distinguish for the first term, because otherwise, the intersection between a empty set and another set is always an empty set
              docs = docs.union(term_docs)
              counter += 1
            else:
              docs = docs.intersection(term_docs)
        except:
            # pass if the term is not in the index
            pass
    docs = list(docs)
    # rank only the docs that keep in docs, so only the docs that contain all the terms in the query
    ranked_docs = rank_documents(query, docs, index, idf, tf, df)
    return ranked_docs # return the ranked docs

def search_in_corpus(query, index, tf, df, idf):
    """
    Apply the ranking
    
    Argument:
    query -- list of terms that we want to search
    index -- inverted index
    tf -- term frequencies
    df -- document frequencies
    idf -- inverted document frequencies
    
    Returns:
    ranked_docs -- list in order of ranked documents
    """

    # 2. apply ranking
    ranked_docs = search_tf_idf(query, index, tf, df, idf) # we call search_tf_idf() for obtaining the ranked documents containing all the terms in that query

    return ranked_docs