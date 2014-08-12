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
import sys, re, itertools, random
sys.path.append('C:/Python27/Lib/site-packages')
fluidsynth.init('/usr/share/sounds/sf2/FluidR3_GM.sf2',"alsa")

def readChordsCSV(filename):
    """ Given the chord data you created already (in a text file), reads
        it into a pandas dataframe. """

    # Import the chord data.
    allchords = pd.read_csv(filename, skiprows=2)[:].sort("Offset")
    allchords.index = xrange(1, len(allchords) + 1)
    with open('oscar2chords.txt', 'rb') as f:
        metmark = float(f.readline())
        tsig_num, tsig_den = [i for i in f.readline().replace(' /', '').split()]
    allchords.sort(columns="Offset", ascending=True)[:10]

    return allchords

def makeChordClf(filename):
    """ Given the filename, reads in chords from that file and then 
    trains a classifier on it. """

    
