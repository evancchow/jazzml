""" Generate the n-grams with NLTK. 
    Question: should I bind notes to rhythm? """

from nltk import bigrams, trigrams, FreqDist
from nltk.collocations import *

def genNGrams(dataList, n=3):
    """ Given a unigram list of notes or chords, generate n-grams 
        (of order(s) n, default n=3) as a list of items and return those. """

    if n == 1: # unigram
        return(dataList)
    elif n == 2:
        return(list(bigrams(dataList)))  
    elif n == 3:
        return(list(trigrams(dataList)))

def genNGramProbs(ngrams):
    """ Given the generated n-grams, return n-gram probabilities as
        a frequency dictionary. """
    ngramFD = FreqDist(ngrams) # frequencies for n-grams
    numNgrams = len(ngrams)
    for k, v in ngramFD.items():
        ngramFD[k] = (ngramFD[k] / float(numNgrams))
    return ngramFD

def sortedNgrams(dataList, n=2):
    """ Given a unigram list of notes or chords, generate n-gram
        collocation finders to return 