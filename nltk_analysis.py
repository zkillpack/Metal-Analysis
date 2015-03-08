import nltk
import csv
import glob
import numpy as np
import pandas as pd
import re
from scipy.spatial.distance import pdist, squareform
import string


# TODO -- process entire corpus, not just a single file...

words = {}
tokenized_posts = {}

def process_tokens(post, current_post):
	global words
	global tokenized_posts
	
	stemmer = nltk.PorterStemmer()
	lemmatizer = nltk.WordNetLemmatizer()
	stopwords = nltk.corpus.stopwords.words("english")

	# Strip, lowercase, tokenize, remove stopwords, stem
	stripped = re.sub('[%s]' % ''.join(string.punctuation), ' ', post)
	tokens = nltk.word_tokenize(stripped)
	tokens = [stemmer.stem(lowercase_token) for lowercase_token in [token.lower() for token in tokens]]
	# Get global and post-specific wordcounts
	for t in tokens:
	 	if t in words:
	 		words[t] = words[t] + 1
	 	else:
	 		words[t] = 1

	if not current_post in tokenized_posts:
		tokenized_posts[current_post] = tokens
	else:
		tokenized_posts[current_post].extend(tokens)



def filter_words():
	# Filter out low frequency counts
	filtered_words = []
	for k in words.keys():
		if words[k] >= 6:
			filtered_words.append(k)
	return filtered_words


for f in glob.glob("folkmetal_po*.csv"):

	with open(f, "r") as csvfile:

		r = csv.reader(csvfile)
		
		# Build vocabulary
		post_count = 0
		post_names = []
		current_post = ""

		for row in r:
			if not current_post == row[0].decode('utf-8'):
				post_count += 1
				current_post = row[0].decode('utf-8')
				post_names.append(row[0].decode('utf-8'))

			process_tokens(row[0].decode('utf-8'), current_post)
			process_tokens(row[1].decode('utf-8'), current_post)

		filtered_words = filter_words()
		
		# Get wordcount vectors for each post (= submissions + comments)
		wordcounts = np.zeros(shape = (post_count, len(filtered_words)), dtype = np.uint8)
		

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
		wordcount_cosines = squareform(pdist(np.transpose(wordcounts), 'cosine'))
		print wordcount_cosines.shape
		print wordcounts.shape

		labeled_word_distances = pd.DataFrame(wordcount_cosines, index = [w.encode('utf-8') for w in filtered_words], columns = [w.encode('utf-8') for w in filtered_words])


		labeled_word_distances.to_csv(f[:-4]+"_processed.csv")

			




		
