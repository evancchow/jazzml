############################################################################
# pipeline.py                                                              #
# Name: Evan Chow                                                          #
# Execution: $ python pipeline.py                                          #
# Description: A client Python program to implement the entire pipeline    #
# (as a demo) from MIDI parsing to music generation, calling the other     #
# modules in the neighboring directories.                                  #
# Data: Pat Metheny MIDI file, w/well-separated melody/accompaniment.      #
#                                                                          #
############################################################################

# Tip for development: write each part in this client program first, then
# move the code to its own module later. That way, you don't have to deal
# with any messy "can't find that var since in another module's
# function" problems, which may slow you down.

# Try to keep your section dividers to one line (""" ... """).

# Defines
head = lambda x: x[0:5] # from R
tail = lambda x: x[:-6:-1] # from R
ppf = lambda n: "%.3f   %s" % (n.offset, n) # pretty print note + offset
trc = lambda s: "%s ..." % (s[0:10]) # pretty print first few chars of str

# Imports
from music21 import *
from collections import defaultdict, OrderedDict
from itertools import groupby, izip_longest
import pygame, copy, sys

# My imports
sys.path.append("./extract")
sys.path.append("./grammar")
# from grammar import parseMelody, unparseGrammar
from grammar import *
from findSolo import findSolo

""" Parse the MIDI data for separate melody and accompaniment parts. """

play = lambda x: midi.realtime.StreamPlayer(x).play()
stop = lambda: pygame.mixer.music.stop()

metheny = converter.parse("andtheniknew_metheny.mid")

# Get melody part, compress into single voice.
# For Metheny piece, Melody is Part #5.
melodyStream = metheny[5]
melody1, melody2 = melodyStream.getElementsByClass(stream.Voice)
for j in melody2:
    melody1.insert(j.offset, j)
melodyVoice = melody1

# FOR REFERENCE
# fullMelody.append(key.KeySignature(sharps=1, mode='major'))

# Bad notes: melodyVoice[370, 391]
# the two B-4, B-3 around melodyVoice[362]. I think: #362, #379
# REMEMBER: after delete each of these, 
# badIndices = [370, 391, 362, 379]
# BETTER FIX: iterate through, if length = 0, then bump it up to 0.125
# since I think this is giving the bug.
for i in melodyVoice:
    if i.quarterLength == 0.0:
        i.quarterLength = 0.25

# Change key signature to adhere to compStream (1 sharp, mode = major).
# Also add Electric Guitar.
melodyVoice.insert(0, instrument.ElectricGuitar())
melodyVoice.insert(0, key.KeySignature(sharps=1, mode='major'))

# The accompaniment parts. Take only the best subset of parts from
# the original data. Maybe add more parts, hand-add valid instruments.
# Should add least add a string part (for sparse solos).
# Verified are good parts: 0, 1, 6, 7
partIndices = [0, 1, 6, 7] # TODO: remove 0.0==inf duration bug in part 7
compStream = stream.Voice()
compStream.append([j.flat for i, j in enumerate(metheny) if i in partIndices])

# Full stream containing both the melody and the accompaniment.
# All parts are flattened.
fullStream = stream.Voice()
for i in xrange(len(compStream)):
    fullStream.append(compStream[i])
fullStream.append(melodyVoice)

# Extract solo stream, assuming you know the positions ..ByOffset(i, j).
# Note that for different instruments (with stream.flat), you NEED to use
# stream.Part(), not stream.Voice().
# Accompanied solo is in range [478, 548)
soloStream = stream.Voice()
for part in fullStream:
    newPart = stream.Part()
    newPart.append(part.getElementsByClass(instrument.Instrument))
    newPart.append(part.getElementsByClass(tempo.MetronomeMark))
    newPart.append(part.getElementsByClass(key.KeySignature))
    newPart.append(part.getElementsByClass(meter.TimeSignature))
    newPart.append(part.getElementsByOffset(476, 548, includeEndBoundary=True))
    np = newPart.flat
    soloStream.insert(np)

# MELODY: Group by measure so you can classify. 
# Note that measure 0 is for the time signature, metronome, etc. which have
# an offset of 0.0.
melodyStream = soloStream[-1]
allMeasures = OrderedDict()
offsetTuples = [(int(n.offset / 4), n) for n in melodyStream]
measureNum = 0 # for now, don't use real m. nums (119, 120)
for key, group in groupby(offsetTuples, lambda x: x[0]):
    allMeasures[measureNum] = [n[1] for n in group]
    measureNum += 1

""" Just play the chord accompaniment with the melody. Refine later. """
""" Think I successfully extracted just the chords in chordStream(). """

# Get the stream of chords.
# offsetTuples_chords: group chords by measure number.
chordStream = soloStream[0]
chordStream.removeByClass(note.Rest)
chordStream.removeByClass(note.Note)
offsetTuples_chords = [(int(n.offset / 4), n) for n in chordStream]

# Generate the chord structure. Use just track 1 (piano) since it is
# the only instrument that has chords. Later, if you have time, you can
# mod this so it works with any MIDI file.
# Group into 4s, just like before.
allMeasures_chords = OrderedDict()
measureNum = 0
for key, group in groupby(offsetTuples_chords, lambda x: x[0]):
    allMeasures_chords[measureNum] = [n[1] for n in group]
    measureNum += 1

# Fix for the below problem.
# 1) Find out why len(allMeasures) != len(allMeasures_chords).
#   ANSWER: resolves at end but melody ends 1/16 before last measure so doesn't
#           actually show up, while the accompaniment's beat 1 right after does.
#           Actually on second thought: melody/comp start on Ab, and resolve to
#           the same key (Ab) so could actually just cut out last measure to loop.
#           Decided: just cut out the last measure.
del allMeasures_chords[len(allMeasures_chords) - 1]

assert len(allMeasures_chords) == len(allMeasures)

# Could make alternative version where everything lined up with beats 1 and 3.


""" Iterate over all measures, generating the grammar strings for each measure. You can do this in non-realtime - because you're just 
    generating the list of clusters.

    Note: since you're just generating cluster patterns, abstractGrammars
    does not strictly HAVE to be the same length as the # of measures, 
    although it would be nice. """

abstractGrammars = []
for ix in xrange(1, len(allMeasures)):
    m = stream.Voice()
    for i in allMeasures[ix]:
        m.insert(i.offset, i)
    c = stream.Voice()
    for j in allMeasures_chords[ix]:
        c.insert(j.offset, j)
    abstractGrammars.append(parseMelody(m, c))

""" 
    
    Take each of these measure-length abstract grammars and cluster
    them into similar groups based on various features (not too many
    since you don't have many observations - maybe 2-3 features at most).

    Features:
    1) Number of notes
    2) Consonance: C = f(x) = a*x1 + b*x2 + ...
        where [a, b, ...] are the coefficients for note type 
        (e.g. 0.8 for chord note, 0.5 for approach note, etc.
        including rests) and [x1, x2, ...] are the note lengths.

    Aim for 3 clusters. Create feature matrix for clustering with K-Means.

"""

from sklearn.cluster import KMeans
import numpy as np

# The coefficients for the different note types.
coefDict = {'C' : 0.8, 'S' : 0.6, 'A' : 0.4,'X' : 0.2, 'R' : 0.1 }

# Extract features for each measure.
features = np.empty([len(abstractGrammars), 2])
for ix, currGrammar in enumerate(abstractGrammars):
    # Test case for one measure. Works just fine.
    numNotes = 0
    consonance = 0.0
    for i in currGrammar.split(' '):
        terms = i.split(',')
        # increment # of notes if it's a note
        if terms[0] != 'R':
            numNotes += 1
        # cumulatively calculate consonance for the measures
        consonance += coefDict[terms[0]] * float(terms[1])
    features[ix, 0] = numNotes
    features[ix, 1] = consonance

# Cluster with KMeans, 3 clusters.
kmeans = KMeans(n_clusters=3)
kmeans.fit(features)
clusterLabels = list(kmeans.labels_)

# Create the clusters as a dictionary for easy access.
clusterDict = defaultdict(list)
for label, grammar in zip(clusterLabels, abstractGrammars):
    clusterDict[label].append(grammar)

""" 

    Real-time generative mode. Now things get crazy! 
    Given your fixed chord progressions (measures w/chords) and the
    chord grammars: cycle through the chord progression one measure
    at a time, for each one choosing a cluster based on N-Gram 
    probabilities and subsequently generating notes accordingly. 
    Test this on one measure first to make sure it works, and
    write in the loop later. 

    Coding tasks:
    1) Create N-Gram generator for the labels.
    2) Cycle through the measures.
        For each measure, generate the next cluster label, & pick random grammar struct from clusterDict vals.
        Then, generate notes for that grammar structure for the measure.

    In other words, in real-time:
    1) take a measure and its chords
    2) generate a cluster for it based on previous cluster(s)
    3) generate notes for that measures for real time use.

    Has to be for indeterminate number of measures so be sure to
    do it on a per-measure basis.

"""

from nltk import bigrams, trigrams, FreqDist
from nltk.collocations import *
from nltk.probability import (ConditionalFreqDist, ConditionalProbDist,
    MLEProbDist, ELEProbDist)
import random

# Create the N-Gram generator object for cluster labels. Will choose
# randomly within each cluster.
grammarGrams = bigrams(clusterLabels)
grammarFreqDist = ConditionalFreqDist(grammarGrams)
grammarProbDist = ConditionalProbDist(grammarFreqDist, MLEProbDist)

""" Note: the measure, chords and all, starts at 0.00. Alter if needed. """

# One measure test: generate a label (based on last label of
# the original dataset, since only one measure here), and create notes
# for it. Test measure = 1st measure of training set.
# In other words: measure #1 of next iteration of training set.
lastLabel = clusterLabels[-1]
m1_chords = stream.Voice()
for i in allMeasures_chords[1]:
    m1_chords.insert((i.offset % 4), i)
m1_label = grammarProbDist[lastLabel].generate()
m1_grammar = random.choice(clusterDict[m1_label]).replace('S', 'C').replace('A','C')
# m1_grammar = clusterDict[m1_label][0]

m1_generated = unparseGrammar(m1_grammar, m1_chords)
    
m = stream.Stream()
m.insert(0, m1_chords)
m.insert(0, m1_generated)

# lastLabel = clusterLabels[-1]
# for measureChords in allMeasures_chords[1]:
#     m_chords = stream.Voice()
#     for mc in measureChords:
#         m_chords.insert((mc.offset % 4), mc)
#     m_label = grammarProbDist[lastLabel].generate()
#     m_grammar = random.choice(clusterDict[m_label]).replace('S', 'C').replace('A','C')
#     m_generated = unparseGrammar(m_grammar, m_chords)
#     m = stream.Stream()
#     m.insert(0, m_chords)
#     m.insert(0, m_generated)
#     lastLabel = m_label