import nltk
import sys

from copy import copy

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> N V | NP VP | N VP | VP NP VP | NP NP | VP NP Conj VP Adv
S -> VP Conj VP | NP NP NP Conj VP NP | NP AP NP NP
NP -> N | Det N | Det N P N | P Det AP | Det Adj N | Det N
NP -> N V | P N | Det Adj N | P Det N
VP -> V | V NP | NP V | Conj N V | N V P | V Det Adv V | N Adv V
VP -> N V P NP | VP Adv | V N P
AP -> Adj V | Det Adj Adj Adj N
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # Tokenize sentence into a list of words
    words = nltk.word_tokenize(sentence)
    
    # Remove any words not including a alphabetical letter
    for word in copy(words):
        if word.isalpha():
            continue
        else:
            words.remove(word)
            
    # Make sure word is in lower case
    new_words = list()
    [new_words.append(word.lower()) for word in words]
    
    return new_words

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np_chunks = list()
    
    # Iterate over all subtrees to check for noun phrases
    for subtree in tree:
        
        # Check if subtree contains noun phrase
        nounPhrase = contains(subtree)
        if not nounPhrase:
            continue
        
        # Check if this is the last NP of the subtree
        contain = False
        for subsubtree in subtree:
            if contains(subsubtree):
                contain = True
                break
        
        # Call the funtion again to move further down the subtree
        if contain:
            current = np_chunk(subtree)
            if current != [] and current not in np_chunks:
                np_chunks.append(current[0])
                    
        # If it is the last NP of the subtree - add it to the NP list
        else:
            np_chunks.append(subtree)

    return np_chunks


def contains(subtree):
    """
    Check if there is a noun phrase further down the three
    """
    # Check if the current node is a noun phrase
    if subtree.label() == "NP":
        return True
    
    # Check if this is the end of the node
    if len(subtree) == 1:
        return False
    
    # Iterate over next subtrees for any noun phrases
    for subsubtree in subtree:
        if contains(subsubtree):
            return True
    
    return False


if __name__ == "__main__":
    main()
