#Ah la la, Ah la la, Gimme Three wishes, I wanna be that Dirtyfinger and his six...
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from textblob import TextBlob
import nltk

import pyLDAvis
import pyLDAvis.sklearn

import numpy as np
import pandas as pd

import unicodedata
import re



def find_polarity(input_text):
    """
    Takes one document and outputs a polarity score. -1 is Very Negative, 1 is Super Positive
    This function should be applied to a column and outputted to a new column.
    """
    return TextBlob(input_text).sentiment.polarity


def find_subjectivity(input_text):
    """
    Takes one document and outputs a subjectivity score. 0 is cold objectivity, 1 is very subjective
    This function should be applied to a column and outputted to a new column.
    """
    return TextBlob(input_text).sentiment.subjectivity


def create_sentiment_df(input_column):
    """
    Accepts a column of text data. Returns a dataframe with the original text with their polarity and 
    subjectivity scores appended to it.
    """
    cols = ['text','polarity','subjectivity']
    df = pd.DataFrame(columns=cols)
    df['text'] = input_column
    df['polarity'] = input_column.apply(find_polarity)
    df['subjectivity'] = input_column.apply(find_subjectivity)
    return df


def create_tfidf_matrix(input_column, max_df=0.8, min_df=2, ngram=(1,1)):
    """
    Creates a feature matrix. Matrix is as wide as the terms that meet the min/max parameters. Each document/row
    will have a tf-idf score for each term.
    Can find ngrams, but has default set to 1-word ngrams. Set ngrams to (1,n) to look for ngrams.
    """
    tfidf_vect = TfidfVectorizer(max_df=max_df, min_df=min_df, stop_words='english', ngram_range=ngram)
    doc_term_matrix = tfidf_vect.fit_transform(input_column.values.astype('U'))
    return doc_term_matrix, tfidf_vect


def create_wordcount_matrix(input_column, max_df=0.8, min_df=2, ngram=(1,1), stop_words='english'):
    """
    Creates a feature matrix. Matrix is as wide as the terms that meet the min/max parameters. Each document/row
    will have a wordcount for each term.
    Can find ngrams, but has default set to 1-word ngrams. Set ngrams to (1,n) to look for ngrams.
    """
    count_vect = CountVectorizer(max_df=max_df, min_df=min_df, stop_words=stop_words, ngram_range=ngram)
    doc_term_matrix = count_vect.fit_transform(input_column.values.astype('U'))
    return doc_term_matrix, count_vect

#USE MATRIX AND VECTORS from last two funcitons as parameters for the next two functions.
# create_tfidf_matrix -> show_nmf_topic_words
# create_wordcount_matrix -> show_LDA_topic_words

def show_LDA_topic_words(matrix, vector, n_topics=5, n_words=5):
    """
    Accepts a doc_term_matrix and a fitted vectorizing model (from previous function). 
    Fits the LDA algorithm to the matrix.
    Uses the features/words from the vectorizing model.
    Prints the top n words for n topics.
    """
    LDA = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    LDA.fit(matrix)
    for i, topic in enumerate(LDA.components_): 
        print(f"Top {n_words} words for topic #{i}:") 
        print([vector.get_feature_names()[i] for i in topic.argsort()[-n_words:]]) 
        print('\n')

def show_nmf_topic_words(matrix, vector, n_topics=5, n_words=5):
    """
    Accepts a doc_term_matrix and a fitted vectorizing model (from previous function). 
    Fits the NMF algorithm to the matrix.
    Uses the features/words from the vectorizing model.
    Prints the top n words for n topics.
    """
    nmf = NMF(n_components=n_topics, random_state=42)
    nmf.fit(matrix )
    for i, topic in enumerate(nmf.components_): 
        print(f"Top {n_words} words for topic #{i}:") 
        print([vector.get_feature_names()[i] for i in topic.argsort()[-n_words:]]) 
        print('\n')


def find_top_documents_per_topic(lda_W, documents,n_docs):
    """
    lda_W is LDA.fit(matrix).transform(matrix)
    n_top_docs is a integer for how many documents you want to represent a topic
    """
    df_W = pd.DataFrame(lda_W, index=documents.index)
    for column in df_W:
        indexes = df_W[column].sort_values().tail(n_docs).index
        print(f'Top {n_docs} Documents for Topic {column}: \n')
        counter = 1
        for i in indexes:
            print(f"Document {counter}")
            print(documents[i] + '\n')
            counter += 1

# def pyLDAvis(input_column, n_topics):
#     matrix, vector = create_tfidf_matrix(input_column, max_df=0.8, min_df=2, ngram=(1,1))
#     LDA = LatentDirichletAllocation(n_components=n_topics, random_state=42)
#     LDA.fit(matrix)
#     pyLDAvis.sklearn.prepare(LDA, matrix, vector)

# def show_pyLDAvis_dashboard(lda_fitted_model, doc_term_matrix, vector):
#     pyLDAvis.sklearn.prepare(lda_fitted_model, doc_term_matrix, vector)


def lemmatize(text):
    """
    accept some text and return the text after applying lemmatization to each word.
    Use with .apply to a Pandas Series
    """
    wnl = nltk.stem.WordNetLemmatizer()
    lemmas = [wnl.lemmatize(word) for word in text.split()]
    return ' '.join(lemmas)

def basic_clean(text):
    """
    Lowercase everything
    Normalize unicode characters
    Replace anything that is not a letter, number, whitespace or a single quote
    """
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    text = re.sub(r"[^a-z0-9'\s]", '', text)
    text = re.sub(r"[\r|\n|\r\n]+", ' ', text)
    return text

def create_corpus(df):
    df_qual = df.select_dtypes(include='object')
    persona_id = df['persona_id']
    df_qual = df_qual.fillna('n/a')
    df_qual = df_qual.astype('str')
    df_qual['big_answer'] = df_qual['research_educ'] + df_qual['research_educ_desc'] + df_qual['how_pick_events'] + df_qual['best_event'] + df_qual['events_attend_recent'] + df_qual['ideal_conference_size'] + df_qual['ideal_structure'] + df_qual['other_conference_types'] + df_qual['ideal_topics'] + df_qual['ideal_attendees'] + df_qual['recommendations']
    df_qual['persona_id'] = persona_id
    return df_qual

def create_persona_corpus(df, persona_n):
    df_qual = df.select_dtypes(include='object')
    persona_id = df['persona_id']
    df_qual = df_qual.fillna('n/a')
    df_qual = df_qual.astype('str')
    df_qual['big_answer'] = df_qual['research_educ'] + df_qual['research_educ_desc'] + df_qual['how_pick_events'] + df_qual['best_event'] + df_qual['events_attend_recent'] + df_qual['ideal_conference_size'] + df_qual['ideal_structure'] + df_qual['other_conference_types'] + df_qual['ideal_topics'] + df_qual['ideal_attendees'] + df_qual['recommendations']
    df_qual['persona_id'] = persona_id
    return df_qual[df_qual.persona_id == persona_n]

# def show_column_keywords(input_column, max_df=.3, min_df=2, ngram_range=(1,3), n_keywords=20, stop_words='english'):
#     """
#     Use a column/Series. Indicate the maximum and minimum amount of documents the words to be anlayzed. And ngram size
#     Returns a list 
#     """
#     input_column = input_column.dropna().apply(basic_clean)
#     input_column = input_column.apply(lemmatize)
#     count_vect = CountVectorizer(max_df=max_df, min_df=min_df, stop_words=stop_words, ngram_range=ngram_range)
#     count_vect.fit_transform(input_column)
#     return list(count_vect.vocabulary_.keys())[:n_keywords]

def assign_topic_column(input_column, max_df=.8, min_df=2, stop_words='english', ngram_range=(1,3), n_components=3):
    """
    takes a pandas column/Series. Runs through the topic modeling pipeline. Assigns the topic_id
    to each row. topic_id with highest probability is assigned.
    """
    input_column = input_column.astype('str')
    input_column = input_column.fillna('nan')
    input_column = input_column.apply(basic_clean)
    input_column = input_column.apply(lemmatize)
    count_vect = CountVectorizer(max_df=max_df, min_df=min_df, stop_words=stop_words, ngram_range=ngram_range)
    doc_term_matrix = count_vect.fit_transform(input_column.values.astype('U'))
    LDA = LatentDirichletAllocation(n_components=n_components, random_state=42)
    LDA.fit(doc_term_matrix)
    lda_H = LDA.transform(doc_term_matrix)
    topic_doc_df = pd.DataFrame(lda_H)
    return topic_doc_df.idxmax(axis=1), topic_doc_df.max(axis=1)

def assign_topic_column_probability(input_column, max_df=.8, min_df=2, stop_words='english', ngram_range=(1,3), n_components=3):
    """
    takes a pandas column/Series. Runs through the topic modeling pipeline. Assigns the topic_id
    to each row. topic_id with highest probability is assigned.
    """
    input_column = input_column.fillna('nan')
    input_column = input_column.astype('str')
    input_column = input_column.apply(basic_clean)
    input_column = input_column.apply(lemmatize)
    count_vect = CountVectorizer(max_df=max_df, min_df=min_df, stop_words=stop_words, ngram_range=ngram_range)
    doc_term_matrix = count_vect.fit_transform(input_column.values.astype('U'))
    LDA = LatentDirichletAllocation(n_components=n_components, random_state=42)
    LDA.fit(doc_term_matrix)
    lda_H = LDA.transform(doc_term_matrix)
    topic_doc_df = pd.DataFrame(lda_H)
    return topic_doc_df.max(axis=1)

def pair_topic_with_text(text_column, topic_column, prob_column, name):
    """
    Takes the raw text column from the wrangle dataframe and the topic column made by the assign_topic function.
    Creates a dataframe with each of the inputs as columns.
    """
    text_column = text_column.reset_index()
    test_df = pd.DataFrame()
    test_df[name + '_text'] = text_column[text_column.columns[1]]
    test_df[name + '_topic_id'] = topic_column
    test_df[name + '_probability'] = prob_column
    return test_df

def find_word_counts(input_column, max_df=.3, min_df=2, ngram_range=(1,3), stop_words='english'):
    """
    Accepts a column of text. Uses default parameters for the WordCount Vectorizer.
    Returns a dataframe with the word list, and their frequency as the other column.
    """
    input_column = input_column.dropna().apply(basic_clean)
    input_column = input_column.apply(lemmatize)
    cv = CountVectorizer(max_df=max_df, min_df=min_df, stop_words=stop_words, ngram_range=ngram_range)   
    blob = cv.fit_transform(input_column)    
    word_list = cv.get_feature_names()    
    count_list = blob.toarray().sum(axis=0)
    word_counts = {'word_list': word_list, 'count_list': count_list}
    df_word_count = pd.DataFrame(data=word_counts)
    return df_word_count

def set_stop_words(stop_words):
    """
    Takes a list of strings. These strings will be appended to the 'english' stop words used in sklearn
    objects that have a stopword parameter.
    Returns a very big list. Assign this to the stopwords parameter in the sklearn objects.
    """
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as esw
    stopWords = stop_words + list(esw) 
    return stopWords

def create_biganswer_col(df):
    """
    Accepts a DataFrame as an input. The dataframe will be reduced to the columns that are of a string/object.
    Nulls will be made into a string value called 'n/a'. Each column is double-checked as a string type
    by using the .astype() method.
    The returned value is a Series that is all the column's values smashed into one column.
    """
    df_quals = df.select_dtypes('object')
    df_quals = df_quals.fillna('n/a')
    df_quals = df_quals.astype('str')
    col_names = list(df_quals.columns)
    list_of_cols = [df_quals[i] for i in col_names]
    big_answer = list_of_cols[13]
    for i in range(len(list_of_cols)-1):
        big_answer = big_answer + list_of_cols[i]
    return big_answer