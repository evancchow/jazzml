""" Generate the n-grams with NLTK. 
    Question: should I bind notes to rhythm? """

from collections import defaultdict
import sys

from nltk import bigrams, trigrams, FreqDist
from nltk.collocations import *
from nltk.probability import ConditionalFreqDist, ConditionalProbDist, ELEProbDist, MLEProbDist

# My imports
sys.path.append('./code/extract/')
sys.path.append('./code/ngram')

def bindNotesLens(ngrams, ngramlens):
    """ Given the generated n-gram notes and the generated n-gram lengths, return
        a list of tuples ((note i, len i), (note i+1, len(i+1))). """
    if isinstance(ngrams[0], list) is True or isinstance(ngrams[0], tuple) is True:
        return [tuple([(i, j) for i, j in zip(notes, lens)]) for notes, lens in zip(ngrams, ngramlens)]
    return [tuple([notes, lens]) for notes, lens in zip(ngrams, ngramlens)]

def bindNotesLens(notes, notelens):
    """ Given two lists [1, 2, 3] and [a, b, c], binds them together as a string.
        For those, you would get; ["1a", "2b", "3c"]. """
    return ["%s,%.2f" % (n, l) for n, l in zip(notes, notelens)]

def noteGenerator(notes, notelens, n):
    """ Return a conditionalprobdist object where:
        cfd[word_i].prob(word_i+1) = the probability of getting
        the bigram (word_i, word_i+1) """

    # Bind notes/lens by considering them 1 word. Unbind later.
    sterms = bindNotesLens(notes, notelens)
    if n == 2:
        ngrams = bigrams(sterms)
    else:
        ngrams = trigrams(sterms)

    # Create the conditional freq/prob dist objects for generating new notes.
    cfdist = ConditionalFreqDist(ngrams)
    cpdist = ConditionalProbDist(cfdist, MLEProbDist)

    # Using this conditionalprobdist object, you can generate new terms.
    return(cpdist)

def generateNotes(noteGenerator, numNotes=30):
    """ Given noteGenerator, a ConditionalProbDist obj., generate new notes
        and return them as a list. 

        Note: You don't use this specifically (since need to base your improv
            on specific chord changes) but good to have just in case you want
            to do totally free jazz improvisation. Maybe could work into small demo? """

    # TODO





