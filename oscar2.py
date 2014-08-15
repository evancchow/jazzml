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

""" Extract raw notes, notes length and raw chords, chord lengths """

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

""" Create the full notes, full chords. Also, create ConditionalProbDist
    object to generate new notes (as a dict kind of format). """

# Note: if you don't feel like coding, stick with it for just 5 minutes.

# The full terms, e.g. "B-3,0.25" in format "note,duration".
fullnotes = bindNotesLens(notes, notelens)

# The generator for new notes/terms.
noteGenerator = noteGenerator(notes, notelens)

""" Build the chord changes. """

