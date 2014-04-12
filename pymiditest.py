from music21 import *

fp = './example.mid'
stream = midi.translate.midiFilePathToStream(fp)
stream