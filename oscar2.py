""" The master client file. Given your well-structured modules in the
    relative subfolders, this Python script from start to finish
    simulates jazz improvisation. 

    Distraction-free mode in Sublime Text 2: shift + F11 (toggle)

    To run from interpreter:
    > from oscar2 import *

    then you can access variables etc.

                                                                """

# Imports
import sys
import pandas as pd
sys.path.append('C:/Python27/Lib/site-packages')
from nltk import *

# My imports
sys.path.append('./code/extract/')
sys.path.append('./code/ngram')
from parseraw import parseRawFile
from generate import *

""" Part 1: Parse the MIDI data, and get the chords/notes into text files. """

# ## Parse the MIDI data.
# ## Note that the filenames can be relative to this script.
filename = './Oscar-Peterson-2.mid'
metronomeNum, timeSig, allChords, allNotes = parseRawFile(filename)

# Notes and lengths, i.e. how long note is.
# Remember to generate the unigrams, bigrams, trigrams and run Text.generate() on them.
notes = [("%s%s" % (i.name, i.octave)) for i in allNotes]
notelens = [i.quarterLength for i in allNotes]

# Chords and lengths, i.e. how long chord is.
# Might want function just for parsing the 
chords = [' '.join(s for s in str(i.sortDiatonicAscending(inPlace=True))
        .replace('<music21.chord.Chord ','')
        .replace('>','').split(' ') if (int(s[-1]) < 6))
         for i in allChords]
chordlens = [i.quarterLength for i in allChords]


""" Generate the N-grams for the notes and chords. 
    Also generate the probabilities for the n-grams. 

    For each n-gram (n=[2, 3]) entry, create probability
    relative to that n-gram total. For example, if there are
    a total of 50 n-grams (w/duplicates) and [i, am] appears twice,
    then the probability for that is 2/50. 

    Then for the actual note generation, you'll pick either unigrams,
    bigrams, or trigrams with weighted probabilites (should chain them
    together for longer passages of notes - for example, bigram
    with elements [a, b] should lead into bigram with elements [b, c]
    where b is shared between both.

    notesNgram = a list of the ngrams (w/duplicates)
    notesNgramProbs = dictionary of unique n-gram, probabilities """

## Unigram notes and probabilities.

## Bigram notes and probabilities.
notesBigram = genNGrams(notes, 2)
# notesBigramProbs = genNGramProbs(notesBigram)

## Trigram notes and probbilities.
notesTrigram = genNGrams(notes, 3)
# notesTrigramProbs = genNGramProbs(notesTrigram)

