""" This module, after you've already created the two files
    *chords.txt and *notes.txt, reads in the chord data, and trains 
    a classifier to fit the notes. Returns the classifier. """

from collections import Counter, defaultdict
from sklearn.cluster import KMeans
from mingus.midi import fluidsynth
from mingus.containers import NoteContainer
from mingus.containers.Bar import Bar
import mingus.core.value as value
import pandas as pd
import numpy as np
import sys, re, itertools, random, cPickle
import scipy.sparse
sys.path.append('C:/Python27/Lib/site-packages')
fluidsynth.init('/usr/share/sounds/sf2/FluidR3_GM.sf2',"alsa")

# Custom modules.
from chordclf_music import *

def readChordsCSV(filename):
    """ Given the chord data you created already (in a text file), reads
        it into a pandas dataframe. """

    # Import the chord data.
    chordData = pd.read_csv(filename, skiprows=2)[:].sort("Offset")
    chordData.index = xrange(1, len(chordData) + 1)
    with open('oscar2chords.txt', 'rb') as f:
        metmark = float(f.readline())
        tsig_num, tsig_den = [i for i in f.readline().replace(' /', '').split()]
    chordData.sort(columns="Offset", ascending=True)[:10]

    return chordData

def makeChordClf(filename_chords, filename_notes):
    """ Reads in chords from that chord, note file and then 
    trains a classifier on it. Main function for other files to call. """

    # Read in chords from CSV, format for the chord prediction / modeling
    chordData = readChordsCSV(filename_chords)
    oscarChords = getChords(chordData)
    oscarChords_string = ""
    for chord in oscarChords:
        for n in chord:
            oscarChords_string += "%s " % n
        oscarChords_string += '\n'

    # Format. Could make more concise here.
    allChords = defaultdict()
    oscarChords_string = oscarChords_string.split('\n')
    for ix, line in enumerate(oscarChords_string):
        items = line.split()
        allChords[ix] = items
    assert len(allChords) == len(set(allChords)) # ensure no duplicate chords

    # Read in Oscar's notes.
    vectors = []
    notedata = pd.read_csv(open(filename_notes, 'rb'), skiprows=2)
    allnotes = []
    for note, octave in zip(notedata["Note/Rest"], notedata["Octave"]):
        allnotes.append("%s%s" % (note, octave))

    # Create bitwise note vectors.
    vectors = np.zeros((1, 88))
    for ix, note in enumerate(allnotes):
        vect = np.zeros((1, 88))
        vect[0, quantify(note)] = 1
        if ix == 0:
            vectors = vect
        else:
            vectors = np.vstack((vectors, vect))

    # Create initial arrays (1-40, one for each thing)
    xdata = np.zeros((1, 88))
    for chordID, chord in allChords.items():
        if chordID == 0:
            xdata = genChordNotes(chord)
        else:
            xdata = np.vstack((xdata, genChordNotes(chord)))
    ydata = allChords.keys()

    print "Before adding random data: ", xdata.shape, len(ydata)

    # create more randomized data
    for chordID, chord in allChords.items():
        for j in xrange(50): 
            xdata = np.vstack((xdata, genChordNotes(chord)))
            ydata.append(chordID)
    ydata = np.array(ydata).reshape(-1, )

    print "After adding random data: ", xdata.shape, ydata.shape


