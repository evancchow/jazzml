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
ppf = lambda n: "%.3f   %s" % (n.offset, n)

# Imports
from music21 import *
from collections import defaultdict, OrderedDict
from itertools import groupby, izip_longest
import pygame, copy, sys

# My imports
sys.path.append("./extract")
sys.path.append("./grammar")
from grammar import grammar
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
melody = soloStream[-1]
allMeasures = OrderedDict()
offsetTuples = [(int(n.offset / 4), n) for n in melody]
measureNum = 0 # for now, don't use real m. nums (119, 120)
for key, group in groupby(offsetTuples, lambda x: x[0]):
    allMeasures[measureNum] = [n[1] for n in group]
    measureNum += 1

""" Just play the chord accompaniment with the melody. Refine later. """
""" Think I successfully extracted just the chords in chordStream(). """
# Generate the chord structure. Use just track 1 (piano) since it is
# the only instrument that has chords. Later, if you have time, you can
# mod this so it works with any MIDI file.
# Group into 4s, just like before.
chordStream = soloStream[0]
chordStream.removeByClass(note.Rest)
chordStream.removeByClass(note.Note)
allMeasures_chords = OrderedDict()
offsetTuples_chords = [(int(n.offset / 4), n) for n in chordStream]
measureNum = 0
for key, group in groupby(offsetTuples_chords, lambda x: x[0]):
    allMeasures_chords[measureNum] = [n[1] for n in group]
    measureNum += 1


""" Create test measure. Won't work immediately for playback because just a
    list of notes (and no metronome mark indicated). """
# TEST: generate the grammar for the first measure. Need to reconvert it
# into a stream since allMeasures stores LISTS of notes and not the
# actual voices themselves.
# For now, though, leave out append instrument, key signature, etc.
# OUTPUT: create a "cluster" for this test measure.
m1 = stream.Voice()
# for i in allMeasures[0]:
#     m1.append(i)
for i in allMeasures[1]:
    m1.insert(i.offset, i) # insert so consistent offsets with original data

# TEST: Get chords for current measure.
c1 = stream.Voice()
for i in allMeasures_chords[1]:
    c1.insert(i.offset, i) # insert so consistent offsets with original data

# def isScaleTone(chord, note):
#     """ Method: generate all scales that have the chord notes using 
#         scale.deriveAll(notelist). Check names ('B-') if note is in those. """

#     # Derive major or minor scales (minor if 'other') based on the quality
#     # of the chord.
#     scaleType = scale.MinorScale()
#     if chord.quality == 'major':
#         scaleType = scale.MajorScale()
#     elif chord.quality == 'minor':
#         scaleType = scale.MinorScale()
#     elif chord.quality == 'augmented':
#         scaleType = scale.WholeToneScale()
#     # Can change later to deriveAll() for flexibility. If so then use list
#     # comprehension of form [x for a in b for x in a].
#     scales = scaleType.derive(chord) # use deriveAll() later for flexibility
#     allPitches = list(set([pitch for pitch in scales.getPitches()]))
#     allNoteNames = [i.name for i in allPitches] # octaves don't matter

#     # Get note name. Return true if in the list of note names.
#     noteName = note.name
#     return (noteName in allNoteNames)

# def isApproachTone(chord, note):
#     """ Method: see if note is +-1 a chord tone. Comment: don't worry about
#         different octaves, since you'll work in the upper-lower bounds for 
#         the next notes anyway (delta 1 3 ...). """

#     for chordPitch in chord.pitches:
#         stepUp = chordPitch.transpose(1)
#         stepDown = chordPitch.transpose(-1)
#         if (note.name == stepDown.name or 
#             note.name == stepDown.getEnharmonic().name or
#             note.name == stepUp.name or
#             note.name == stepUp.getEnharmonic().name):
#                 return True
#     return False

# # Information for the start measure.
# measureStartTime = m1[0].offset - (m1[0].offset % 4) # meas. start, i.e.476.0
# measureStartOffset  = m1[0].offset - measureStartTime # how long til note #1

# # Information for previous note.
# prevNote = None
# numNonRests = 0 # number of non-rest elements in the measure.
# for ix, nr in enumerate(m1):
#     """ Iterate over the notes and rests in m1, finding the grammar and
#         writing it to a string. """

#     # FIRST, get type of note, e.g. R for Rest, C for Chord, etc.
#     # Dealing with solo notes here. If unexpected chord: still call 'C'.
#     elementType = ' '
#     lastChord = [n for n in c1 if n.offset <= nr.offset][-1]
#     # R: First, check if it's a rest. Clearly a rest --> only one possibility.
#     if isinstance(nr, note.Rest):
#         elementType = 'R'
#     # C: Next, check to see if note pitch is in the last chord.
#     elif nr.name in lastChord.pitchNames or isinstance(nr, chord.Chord):
#         elementType = 'C'
#     # L: (Complement tone) Skip this for now.
#     # S: Check if it's a scale tone.
#     elif isScaleTone(lastChord, nr):
#         elementType = 'S'
#     # A: Check if it's an approach tone, i.e. +-1 halfstep chord tone.
#     elif isApproachTone(lastchord, nr):
#         elementType = 'A'
#     # X: Otherwise, it's an arbitrary tone. Generate random note.
#     else:
#         elementType = 'X'

#     # SECOND, get the length for each element. e.g. 8th note = R8, but
#     # to simplify things you'll use the direct num, e.g. R,0.125
#     if (ix == (len(m1)-1)):
#         # formula for a in "a - b": start of measure (e.g. 476) + 4
#         diff = measureStartTime + 4.0 - nr.offset
#     else:
#         diff = m1[ix + 1].offset - nr.offset

#     # Combine into the note info.
#     noteInfo = "%s,%.3f" % (elementType, diff)

#     # THIRD, get the deltas (max range up, max range down) based on where
#     # the previous note was, +- minor 3. Skip rests (don't affect deltas).
#     intervalInfo = ""
#     if isinstance(nr, note.Note):
#         numNonRests += 1
#         if numNonRests == 1:
#             prevNote = nr
#         else:
#             noteDist = interval.Interval(noteStart=prevNote, noteEnd=nr)
#             noteDistUpper = interval.add([noteDist, "m3"])
#             noteDistLower = interval.subtract([noteDist, "m3"])
#             intervalInfo = "<%s,%s> " % (noteDistUpper.directedName, 
#                 noteDistLower.directedName)
#             prevNote = nr

#     # Return. Do lazy evaluation for real-time performance.
#     grammarTerm = noteInfo + intervalInfo
#     print grammarTerm

