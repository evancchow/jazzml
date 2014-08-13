""" The master client file. Given your well-structured modules in the
    relative subfolders, this Python script from start to finish
    simulates jazz improvisation. 

    Distraction-free mode in Sublime Text 2: shift + F11 (toggle)

                                                                """

# Imports
import sys
import pandas as pd
sys.path.append('./code/extract/')
sys.path.append('./code/ngram')
from parseraw import parseRawFile
from chordclf import makeChordClf
from generate import genNGrams

from chordclf_music import mingifytext
from mingus.midi import fluidsynth
sys.path.append('C:/Python27/Lib/site-packages')

""" Part 1: Parse the MIDI data, and get the chords/notes into text files. """

# ## Parse the MIDI data.
# ## Note that the filenames can be relative to this script.
filename = './Oscar-Peterson-2.mid'
metronomeNum, timeSig, allChords, allNotes = parseRawFile(filename)

# ## Write out notes to a text file. 
# ## Ideally, you'll be able to keep everything
# ## in RAM eventually, so no need for intermediate text files.
with open('oscar2notes.txt', 'wb') as f:
    f.write("%s\n" % metronomeNum)
    f.write("%s\n" % timeSig)
    f.write("Note/Rest,Octave,Len,Offset\n")
    for i in allNotes:
        f.write("%s,%s,%s,%s\n" % (i.name, 
            i.octave, i.quarterLength, float(i.offset)))

# ## Write out chords to a text file.
with open('oscar2chords.txt', 'wb') as f:
    f.write("%s\n" % metronomeNum)
    f.write("%s\n" % timeSig)
    f.write("FullName,CommonName,Len,Offset\n")
    for i in allChords:
        f.write("%s,%s,%s,%s\n" % (i.fullName,
            i.pitchedCommonName, i.quarterLength, float(i.offset)))

""" Re-read in the notes, generate n-grams, etc. """

## Read in the chords to get the classifier and the chord dictionary.
filename_chords = 'oscar2chords.txt'
filename_notes = 'oscar2notes.txt'
grid_search, chordDict = makeChordClf(filename_chords, filename_notes)

## Read in oscar's notes again.
oscar2 = pd.read_csv('oscar2notes.txt', skiprows=2)[:].sort("Offset")
oscar2.index = xrange(1, len(oscar2) + 1)
oscar2 = oscar2[oscar2.Octave >= 4] # threshold >= octave 4 for melodies
with open('oscar2notes.txt', 'rb') as f:
    metmark = float(f.readline())
    tsig_num, tsig_den = [i for i in f.readline().replace(' /', '').split()]

## Generate the n-grams.
ngrams = genNGrams(oscar2)
