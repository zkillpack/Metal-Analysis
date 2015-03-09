import nltk
import csv
import glob
import numpy as np
import pandas as pd
import re
from scipy.spatial.distance import pdist, squareform
import string
import heapq

# Stem and lemmatize tokens
stem = False

# Process all subreddits individually or at once
at_once = False

words = {}
tokenized_posts = {}

stemmer = nltk.PorterStemmer()
lemmatizer = nltk.WordNetLemmatizer()
stopwords = nltk.corpus.stopwords.words("english")


def process_tokens(post, current_post):
    global words
    global tokenized_posts

    # Strip, lowercase, tokenize, remove stopwords, stem
    stripped = re.sub('[%s]' % ''.join(string.punctuation), '', post)
    tokens = nltk.word_tokenize(stripped)
    tokens = [token for token in tokens if not token in stopwords]
    tokens = [token.lower() for token in tokens]
    if stem:
        tokens = [
            lemmatizer.lemmatize(stemmer.stem(token)) for token in tokens]

    # Get wordcounts
    for token in tokens:
        if token in words:
            words[token] = words[token] + 1
        else:
            words[token] = 1

    if not current_post in tokenized_posts:
        tokenized_posts[current_post] = tokens
    else:
        tokenized_posts[current_post].extend(tokens)


def filter_words():
    # Filter out low frequency counts
    filtered_words = []
    for k in words.keys():
        if words[k] >= 10:
            filtered_words.append(k)
    return filtered_words


post_count = 0
post_names = []

for f in glob.glob("processed/*.csv"):
    print f

    if not at_once:
        global words
        global tokenized_posts
        words = {}
        tokenized_posts = {}
        post_count = 0
        post_names = []

    with open(f, "r") as csvfile:

        r = csv.reader(csvfile)

        # Build vocabulary
        current_post = ""

        for row in r:
            if not current_post == row[0].decode('utf-8'):
                post_count += 1
                current_post = row[0].decode('utf-8')
                post_names.append(row[0].decode('utf-8'))

            process_tokens(row[0].decode('utf-8'), current_post)
            try:
                process_tokens(row[1].decode('utf-8'), current_post)
            except:
                print row, current_post



        if not at_once:
            filtered_words = filter_words()

            # Get wordcount vectors for each post (= submissions + comments)
            wordcounts = np.zeros(
                shape=(post_count, len(filtered_words)), dtype = np.uint8)

            word_index = {}
            for i, word in enumerate(filtered_words):
                word_index[word] = i

            for i, post in enumerate(tokenized_posts):
                for token in tokenized_posts[post]:
                    token_index = word_index.get(token)
                    # Only process tokens above the wordcount threshold!
                    if token_index >= 0:
                        wordcounts[i][token_index] += 1

            # Labeled bag-of-words files into a csv
        
        
            wordcount_cosines = squareform(
                pdist(np.transpose(wordcounts), 'cosine'))

            labeled_word_distances = pd.DataFrame(wordcount_cosines, index=[w.encode(
                'utf-8') for w in filtered_words], columns=[w.encode('utf-8') for w in filtered_words])


            labeled_word_distances.to_csv("analyzed" + f[9:-4] + "_processed.csv")


if at_once:
    # If all at once, do the gephi processing all at once to avoid unncessary computations
    N = 5
    filtered_words = filter_words()

    # Get wordcount vectors for each post (= submissions + comments)

    wordcounts = np.zeros(
    shape=(post_count, len(filtered_words)), dtype = np.uint8)

    word_index = {}
    for i, word in enumerate(filtered_words):
        word_index[word] = i

    for i, post in enumerate(tokenized_posts):
        for token in tokenized_posts[post]:
            token_index = word_index.get(token)
            # Only process tokens above the wordcount threshold!
            if token_index >= 0:
                wordcounts[i][token_index] += 1

    # Labeled bag-of-words files into a csv

    print wordcounts.shape
    wordcount_cosines = squareform(
    pdist(np.transpose(wordcounts), 'cosine'))

   
    print wordcount_cosines.shape

    w = csv.writer(open("gephi/all.csv", "w"))
    w.writerow(["Source", "Target", "Weight"])

    pairs = set()
    row_accum = []
    

    for i, row in labeled_word_distances.iterrows():
        print 5
        row_accum = []
        current_word = i
        for j, val in enumerate(row):
            if i == 0:
                continue
            else:
                if j == 0:
                    continue
                else:
                    heapq.heappush(row_accum, (1 - float(val), filtered_words[j]))

        strongest_links = heapq.nlargest(N, row_accum, lambda x: x[0])

        for link in strongest_links:
            # ignore duplicates
            if(link[1], current_word) in pairs:
                continue
            pairs.add((current_word, link[1]))
            print link
            w.writerow([current_word.encode("utf-8"), link[1].encode("utf-8"), "%.3f" % link[0]])