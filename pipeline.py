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

# Imports
from music21 import *
from collections import defaultdict
import pygame, copy, sys

# My imports
sys.path.append("./extract")
sys.path.append("./grammar")
from grammar import grammar

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

fullMelody = stream.Part() # Stream for the melody
fullMelody.append(instrument.ElectricGuitar())
fullMelody.append(key.KeySignature(sharps=1, mode='major'))
fullMelody.append(meter.TimeSignature())
fullMelody.append(melody1)
melodyVoice = fullMelody.getElementsByClass(stream.Voice)[0]

# # TODO later; figure out how to get bass drum to play on midi.
# # At worst, you have two options: 1) remove the offending track
# # 2) find another way to encode the track (e.g. MIDI module)

# # Remove melody to make original data the accompaniment.
compStream = metheny
compStream.remove(melodyStream)

""" Generate abstract melodies for each measure. """

# Test your algorithm first.
# Get first few bars of melody. Not sure of good way to subset the
# fullMelody Stream.
test = stream.Part()
# test = melodyVoice[0:20]
test.append(instrument.ElectricGuitar())
test.append(meter.TimeSignature())
test.append(key.KeySignature(sharps=1, mode='major'))
test.append(melodyVoice[20:30])

testMelody = melodyVoice[20:30]

# grammar(testMelody)
