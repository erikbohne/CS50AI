import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    corpus = dict()
    
    # Iterate over all files in directory and add to the dictionary
    for file in os.listdir(directory):
        
        # Open file to read content
        with open((os.path.join(directory, file))) as f:
            text = f.read()
        
        # Add key and text to dictionary
        corpus[file] = text
    
    return corpus
        

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """    
    # Tokenize the text using nltk library
    tokenized = nltk.word_tokenize(document)

    # Filter out stopwords and punctuations and lowercase all words
    fixed_list = list()
    for word in tokenized:
        if word in nltk.corpus.stopwords.words("english"):
            continue
        elif word in string.punctuation:
            continue
        else:
            fixed_list.append(word.lower())
    
    return fixed_list
    
def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    
    # Get a set of all the words across all documents
    words = set()
    for document in documents:
        words.update(documents[document])
    
    # Create dict to store all idfs
    idfs = dict()
    for word in words:
        frequency = sum(word in documents[document] for document in documents)
        idf = math.log(len(documents) / frequency)
        idfs[word] = idf
    
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # Calculate term frequency for the queried words
    tf_idfs = dict()
    for file in files:
        tf_idfs[file] = list()
        for word in query:
            frequency = files[file].count(word)
            if frequency > 0:
                tf_idfs[file].append((word, frequency * idfs[word]))
    
    # Calculate relevancy of files
    valued_files = dict()
    for file in files:
        valued_files[file] = sum(tf_idfs[file][i][1] for i in range(len(tf_idfs[file])))

    # Sort dict by values
    valued_files = dict(sorted(valued_files.items(), key=lambda item: item[1], reverse=True))
    
    # Return a list of top files with n number of top files
    return list(valued_files.keys())[:n]
        
    
def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """    
    # Calcualte idfs sum for every sentence in the file
    idfs_sum = dict()
    for sentence in sentences:
        current = sum(idfs[word] for word in sentences[sentence] if word in query)
        idfs_sum[sentence] = current
    
    # Sort sentences by idfs value
    sorted_sentences = sorted(idfs_sum.items(), key=lambda item: item[1], reverse=True)
            
    # Add all sentences with the max value, density sort them and check if number of sentences
    # match "SENTENCES_MATCHES" variable. If not, do it again with next idf value.
    max_sentences = list()
    while len(max_sentences) < n:
        dens_sentences = dict()
        max_value = sorted_sentences[len(max_sentences)][1]
        for sentence in add_sentences(sorted_sentences, max_value):
            dens_sentences[sentence] = sum(
                word in sentences[sentence] for word in query
                ) / len(sentences[sentence])
            density_sorted = dict(sorted(dens_sentences.items(), key=lambda item: item[1], reverse=True))
            
        for sentence in density_sorted.keys():
            max_sentences.append(sentence)
    
    return max_sentences[:n]
        
def add_sentences(sorted_sentences, value):
    """
    Returns all sentences with a given idfs value
    """
    sentences = list()
    for i in range(len(sorted_sentences)):
        if sorted_sentences[i][1] == value:
            sentences.append(sorted_sentences[i][0])
            continue
        elif sorted_sentences[i][1] < value:
            break
    
    return sentences
            
if __name__ == "__main__":
    main()
