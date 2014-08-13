""" Script with various helper functions to generate the N-Grams. """

from collections import Counter, defaultdict
from sklearn.cluster import KMeans, Ward, AffinityPropagation
from itertools import izip, izip_longest, groupby
import music21
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys, re, itertools, random, copy
sys.path.append('C:/Python27/Lib/site-packages')

""" 1. Get generated notes based on the trigram model. """

# Iterate over a list in chunks of size n. Return tuples (for dict).
def chunks(iterable, n):
    for ix, item in enumerate(iterable):
        if ix == len(iterable) - (n-1): return
        yield tuple(iterable[ix:ix+n])

# Build the conditional probability tables.
def condProbTables(ngramfreqs, nngramfreqs):
    nprobs = defaultdict(int)
    prevnngramnexts = defaultdict(list)
    for ngram, freq in ngramfreqs.items():
        prevnngram = ngram[:-1]
        currchar = ngram[-1]
        nprobs[(currchar, prevnngram)] = float(ngramfreqs[ngram]) / nngramfreqs[prevnngram]
        if prevnngram not in prevnngramnexts.keys():
            prevnngramnexts[prevnngram].extend([(currchar, (float(ngramfreqs[ngram]) / nngramfreqs[prevnngram]))])
            continue
        prevnngramnexts[prevnngram].extend([(currchar, (float(ngramfreqs[ngram]) / nngramfreqs[prevnngram]))])
    return nprobs, prevnngramnexts
    
# Yield the next note for a given n-gram model.
# 'unitsize' is n, i.e. 3 for using trigrams.
# args are the previous notes used to generate the next one.
# Assumes # of args == same # for lookup in prevnnnexts
def yieldNext(prevnnexts, *args):
    lookup = tuple([a for a in args])
    nexts = np.array(prevnnexts[lookup])
    nextnotes = nexts[:,0]
    probabilities = nexts[:,1]

    # remove possibility of >= 3 notes in row for trigram model
    if len(set(args)) == 1: # if prev notes = all same
        ixToDel = []
        for ix, (note, prob) in enumerate(zip(nextnotes, probabilities)):
            if note in args:
                ixToDel.append(ix)
        nextnotes = np.delete(nextnotes, ixToDel)
        probabilities = np.delete(probabilities, ixToDel)
                
    # Also to consider: remove notes in nextnotes if jump from octave 4 to 6 etc.
    totalprob = 0; # assert is normalized
    for p in probabilities: totalprob += float(p)
    if totalprob != 1.0: probabilities = normList(probabilities)
    return np.random.choice(nextnotes, p=probabilities)

# Generate k trigrams; default is 100. Change # of trigrams here.
def genTrigrams(prevbigramnexts, k=100):
    note1 = "start"
    note2 = "start"
    note3 = note2
    for i in xrange(k):
        note3 = yieldNext(prevbigramnexts, note1, note2)
        note1 = note2
        note2 = note3
        yield note3

# Generate k trigrams; default is 100. Change # of trigrams here.
def genQuadgrams(prevtrigramnexts, k=100):
    note1 = "start"
    note2 = "start"
    note3 = "start"
    note4 = note3
    for i in xrange(k):
        note4 = yieldNext(prevtrigramnexts, note1, note2, note3)
        note1 = note2
        note2 = note3
        note3 = note4
        yield note4
        
""" 2. Generate the offsets using simple frequency probabilities. """

# Iterate over iterable in groups of n.
def grouper(n, iterable, fillvalue=None):
    for ix, i in enumerate(iterable):
        if ix == len(iterable) - 1:
            break
        yield (iterable[ix], iterable[ix+1])
        
# Normalize an iterable.
def normList(L, normalizeTo=1):
    vMax = 0
    for item in L:
        vMax += float(item)
    return [ float(x)/(vMax*1.0)*normalizeTo for x in L]

# Round to nearest nth of a unit.
def my_round(x, n=4):
    return round(x*n)/n

""" 3. Pruning. 
    For one, go through and make sure you don't get random tiny clusters 
    of notes + awkward octave jumps. If you have time later, do this dynamically 
    in generating the n-gram models above. 
    Assume Oscar doesn't play any repeated notes at his
    ridiculously fast tempo (since consequence of n-gram model anyway). """

# Given a MUSIC21 note, such as C5 or D#7, convert it
# into a note on the keyboard between 0 and 87 inclusive.
def quantify(note):
    notevals = {
        'C' : 0,
        'D' : 2,
        'E' : 4,
        'F' : 5,
        'G' : 7,
        'A' : 9,
        'B' : 11
    }
    quantized = 0
    octave = int(note[-1]) - 1
    for i in note[:-1]:
        if i in notevals: quantized += notevals[i]
        if i == '-': quantized -= 1
        if i == '#': quantized += 1
    quantized += 12 * octave
    return quantized

# iterate through, remove if awkward jumps i.e. c6 b4 g4 e4 f6
def findJumps(gennotes):
    ixJumps = []
    for ix, note in enumerate(gennotes):
        if ix == len(gennotes) - 2:
            break
        currOct = note[-1]
        nextOct = gennotes[ix+1][-1]
        if np.abs(float(currOct) - float(nextOct)) > 1:
            ixJumps.append(ix)
    return ixJumps

# Find jumps > 1 octave in the generated notes, and change so jump <= 1 oct.
# For example, if have c4 g4 c6, changes g4 to g5.
# Doesn't change original style too much, but solves n-gram problem noted in past literature.
def smoothen(original):
    gennotes = copy.deepcopy(original)
    ixJumps = findJumps(gennotes)
    for i in ixJumps:
        if i == len(gennotes) - 1:
            break
        prevnote = gennotes[i]
        nextnote = gennotes[i+1]
        prevoct = float(prevnote[-1])
        nextoct = float(nextnote[-1])
        if prevoct > nextoct:
            gennotes[i] = "%s%s" % (prevnote[:-1], int(prevnote[-1]) - 1)
        elif prevoct < nextoct:
            gennotes[i+1] = "%s%s" % (nextnote[:-1], int(nextnote[-1]) - 1)
    return gennotes

# Given the generated notes, removes duplicates
# For example, c4 g5 g5 g5 e5 -> c4 g5 e5.
def rmDuplicates(original):
    gennotes = copy.deepcopy(original)
    i = 0
    while i < len(gennotes) - 1:
        if gennotes[i] == gennotes[i+1]:
            del gennotes[i]
        else:
            i += 1
    return gennotes

# Given the generated notes, remove isolated notes w/jumps too far apart.
# For example, c6 g4 c6 --> c6 c6. only if adjacent = same octave
# since say c6 g5 c4 could make good sense. (Run rmDup. again after this)
def rmSingles(original):
    gennotes = copy.deepcopy(original)
    ixToDel = []
    i = 0
    while i < len(gennotes) - 1:
        if i == 0: i+=1; continue
        prevnote = gennotes[i-1]
        currnote = gennotes[i]
        nextnote = gennotes[i+1]
        if (prevnote[-1] == nextnote[-1] and np.abs(float(prevnote[-1]) - float(currnote[-1])) > 0):
            gennotes.pop(i)
        i+=1
    return gennotes

# Remove half notes. Experimental use only.
def rmHalfNotes(original):
    gennotes = copy.deepcopy(original)
    ixToDel = []
    length = len(gennotes)
    for ix in xrange(length):
        if ix == length - 1:
            break
        if np.abs(quantify(gennotes[ix]) - quantify(gennotes[ix+1])) == 1:
            ixToDel.append(ix)
    gennotes = [i for ix, i in enumerate(gennotes) if ix not in ixToDel]
    return gennotes

""" The main function to generate the n-grams. """

def genNGrams(oscar2):
    """ Generate the n-grams. oscar2 is a dataframe:
        Note/Rest | Octave | Len      | Offset
        D           5        0.750000   12.666
        ... 
        Feed in the dataframe to this function, and it will
        return the n-grams as a list of tuples (note, offset). """

    """ The script to generate the notes."""

    # Iterates over rows, where each element in the iterable is twofold: 
    # element[0] = the index, element[1] = the note object
    possiblenotes = ["%s%s" % (row[1]["Note/Rest"], 
        row[1]["Octave"]) for row in oscar2.iterrows()]
    possiblenotes.insert(0, "start")
    possiblenotes.insert(0, "start")
    possiblenotes.insert(0, "start")

    # Get trigram probabilities.
    bigramfreqs = defaultdict(int)
    for i in chunks(possiblenotes, 2):
        bigramfreqs[i] += 1
    trigramfreqs = defaultdict(int)
    for i in chunks(possiblenotes, 3):
        trigramfreqs[i] += 1
    quadgramfreqs = defaultdict(int)
    for i in chunks(possiblenotes, 4):
        quadgramfreqs[i] += 1
        
    # Encode ngram probabilities
    triprobs, prevbigramnexts = condProbTables(trigramfreqs, bigramfreqs)
    # quadprobs, prevtrigramnexts = condProbTables(quadgramfreqs, trigramfreqs)

    """ The offsets. """

    offsets = defaultdict(int)
    genTuples = grouper(2, [float(i) for i in oscar2["Offset"]])
    for j in genTuples:
        toCompare = j
        diff = float(toCompare[1]) - float(toCompare[0])
        diff = my_round(diff)
        if diff > 4: continue # can't have gaps > 4
        offsets[diff] += 1 # set gaps nicely, only integer gaps.
        
    offset_poss = [k for k in offsets]           # possible offsets. need separate for np.random.choice()
    offset_probs = [offsets[k] for k in offsets] # probabilities for each of those offset

    # prune offsets after normalizing so # possible offsets < 32 for np.random.choice()
    # durations: cutoff if over 6
    offset_ixToDel = [jx for jx, j in enumerate(offset_probs) if j < 5 and (offset_poss[jx] < 2)]
    offset_poss = [i for ix, i in enumerate(offset_poss) if ix not in offset_ixToDel]
    offset_probs = [j for jx, j in enumerate(offset_probs) if jx not in offset_ixToDel]
    for jx, j in enumerate(offset_poss):
        if j <= 0:
            del offset_poss[jx]
            del offset_probs[jx]
    offset_probs = normList(offset_probs)

    # Cheap fix since too lazy to debug: generate n-grams, if not right number, redo.
    numberofngrams = 200 # Do 300-400 notes for the presentation. 1350 ~= # of oscar's original notes
    numberGenerated = 0;
    gennotes, genoffsets = [], []
    while numberGenerated != numberofngrams: # remove while if decide to rm. duplicates
        try: 
    #         gennotes = list(note for note in genQuadgrams(prevtrigramnexts, numberofngrams) if note != "start")
            gennotes = list(note for note in genTrigrams(prevbigramnexts, numberofngrams) if note != "start")
            genoffsets = list(np.random.choice(offset_poss, p=offset_probs) for i in xrange(len(gennotes)))
        except IndexError: 
    #         gennotes = list(note for note in genQuadgrams(prevtrigramnexts, numberofngrams) if note != "start")
            gennotes = list(note for note in genTrigrams(prevbigramnexts, numberofngrams) if note != "start")
            genoffsets = list(np.random.choice(offset_poss, p=offset_probs) for i in xrange(len(gennotes)))
        numberGenerated = len(gennotes)

    # Prune. Experiment with which to use, to see how close is to Oscar's style.
    # Demonstrating pruning in your presentation!
    gennotes = smoothen(gennotes)
    gennotes = rmDuplicates(gennotes)
    gennotes = rmSingles(gennotes)
    gennotes = rmDuplicates(gennotes)

    # Assert that you got the right # of notes.
    return ((note, length) for note, length in zip(gennotes, genoffsets))
    # print "# of notes generated after pruning: %s" % len(gennotes)
    # with open("oscar2ngrams.txt", 'wb') as f:
    #     for note, length in zip(gennotes, genoffsets):
    #         f.write("%s,%s\n" % (note, length))