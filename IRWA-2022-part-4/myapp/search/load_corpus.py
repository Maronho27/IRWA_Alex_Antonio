import pandas as pd

from myapp.core.utils import load_json_file, load_name_docs
from myapp.search.objects import Document

_corpus = {}


def load_corpus(path, path_2) -> [Document]:
    """
    Load file and transform to dictionary with each document as an object for easier treatment when needed for displaying
    in results, stats, etc.

    Arguments:
    path: path of the JSON containing the tweets
    path_2: path of the CSV containing the name of each tweet

    Returns:
    _corpus: Document object containing information of each tweet
    """
    df = _load_corpus_as_dataframe(path, path_2)
    df.apply(_row_to_doc_dict, axis=1)
    return _corpus


def _load_corpus_as_dataframe(path, path_2):
    """
    Load documents corpus from file in 'path' and path_2

    Arguments:
    path: path of the JSON containing the tweets
    path_2: path of the CSV containing the name of each tweet

    Returns:
    corpus: DataFrame containing information of each tweet
    """
    json_data = load_json_file(path)
    doc_id = load_name_docs(path_2)
    tweets_df = _load_tweets_as_dataframe(json_data)

    # change the id for the correct name stored in doc_id
    for i, row in tweets_df.iterrows():
        tweets_df.loc[i, "id"] = doc_id[str(tweets_df.loc[i, "id"])]

    _clean_hashtags_and_urls(tweets_df)

    # Rename columns to obtain: Tweet | Username | Date | Hashtags | Likes | Retweets | Url | Language
    corpus = tweets_df.rename(
        columns={"id": "Id", "full_text": "Tweet", "screen_name": "Username", "created_at": "Date",
                 "favorite_count": "Likes",
                 "retweet_count": "Retweets", "lang": "Language"})

    # select only interesting columns
    filter_columns = ["Id", "Tweet", "Username", "Date", "Hashtags", "Likes", "Retweets", "Url", "Language"]
    corpus = corpus[filter_columns]
    return corpus


def _load_tweets_as_dataframe(json_data):
    """
    Returns a first version of the documents corpus

    Arguments:
    json_data: tweets in a JSON format

    Returns:
    data: First version of the DataFrame containing the tweets
    """
    data = pd.DataFrame(json_data)
    # parse entities as new columns
    data = pd.concat([data.drop(['entities'], axis=1), data['entities'].apply(pd.Series)], axis=1)
    # parse user data as new columns and rename some columns to prevent duplicate column names
    data = pd.concat([data.drop(['user'], axis=1), data['user'].apply(pd.Series).rename(
        columns={"created_at": "user_created_at", "id": "user_id", "id_str": "user_id_str", "lang": "user_lang"})],
                     axis=1)
    return data


def _build_tags(row):
    """
    Returns the hashtags of each tweet

    Arguments:
    row: tweet

    Returns:
    url: Hashstags of each tweet
    """
    tags = []
    # for ht in row["hashtags"]:
    #     tags.append(ht["text"])
    for ht in row:
        tags.append(ht["text"])
    return tags


def _build_url(row):
    """
    Returns the URL of each tweet

    Arguments:
    row: tweet

    Returns:
    url: URL of the tweet
    """
    url = ""
    try:
        url = row["entities"]["url"]["urls"][0]["url"]  # tweet URL
    except:
        try:
            url = row["retweeted_status"]["extended_tweet"]["entities"]["media"][0]["url"]  # Retweeted
        except:
            url = ""
    return url


def _clean_hashtags_and_urls(df):
    """
    Collect the hashtags and URL if they have not been correctly collected before

    Arguments:
    df: DataFrame with the tweets

    Returns:
    df: DataFrame with the Hashtags and URL cleaned
    """
    df["Hashtags"] = df["hashtags"].apply(_build_tags)
    df["Url"] = df.apply(lambda row: _build_url(row), axis=1)
    df.drop(columns=["entities"], axis=1, inplace=True)


def load_tweets_as_dataframe2(json_data):
    """Load json into a dataframe

    Parameters:
    path (string): the file path

    Returns:
    DataFrame: a Panda DataFrame containing the tweet content in columns
    """
    # Load the JSON as a Dictionary
    tweets_dictionary = json_data.items()
    # Load the Dictionary into a DataFrame.
    dataframe = pd.DataFrame(tweets_dictionary)
    # remove first column that just has indices as strings: '0', '1', etc.
    dataframe.drop(dataframe.columns[0], axis=1, inplace=True)
    return dataframe


def load_tweets_as_dataframe3(json_data):
    """Load json data into a dataframe

    Parameters:
    json_data (string): the json object

    Returns:
    DataFrame: a Panda DataFrame containing the tweet content in columns
    """

    # Load the JSON object into a DataFrame.
    dataframe = pd.DataFrame(json_data).transpose()

    # select only interesting columns
    filter_columns = ["id", "full_text", "created_at", "entities", "retweet_count", "favorite_count", "lang"]
    dataframe = dataframe[filter_columns]
    return dataframe


def _row_to_doc_dict(row: pd.Series):
    """
    Convert each row of the DataFrame into an Object of class Document

    Arguments:
    row: tweet

    Returns:
    _corpus[row['Id']]: Document Object of the row
    """
    _corpus[row['Id']] = Document(row['Id'], row['Tweet'][0:100], row['Tweet'], row['Date'], row['Likes'],
                                  row['Retweets'],
                                  row['Url'], row['Hashtags'])
