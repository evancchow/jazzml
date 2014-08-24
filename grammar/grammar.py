#################################################################
# grammar.py
# Name: Evan Chow
# Description: generates a string representation of the measures
# in a melody stream.
#
##################################################################

from collections import OrderedDict, defaultdict
from itertools import groupby
from music21 import *
import copy

# Helper method.
def isScaleTone(chord, note):
    """ Method: generate all scales that have the chord notes using 
        scale.deriveAll(notelist). Check names ('B-') if note is in those. """

    # Derive major or minor scales (minor if 'other') based on the quality
    # of the chord.
    scaleType = scale.MinorScale()
    if chord.quality == 'major':
        scaleType = scale.MajorScale()
    elif chord.quality == 'minor':
        scaleType = scale.MinorScale()
    elif chord.quality == 'augmented':
        scaleType = scale.WholeToneScale()
    # Can change later to deriveAll() for flexibility. If so then use list
    # comprehension of form [x for a in b for x in a].
    scales = scaleType.derive(chord) # use deriveAll() later for flexibility
    allPitches = list(set([pitch for pitch in scales.getPitches()]))
    allNoteNames = [i.name for i in allPitches] # octaves don't matter

    # Get note name. Return true if in the list of note names.
    noteName = note.name
    return (noteName in allNoteNames)

# Helper method.
def isApproachTone(chord, note):
    """ Method: see if note is +-1 a chord tone. Comment: don't worry about
        different octaves, since you'll work in the upper-lower bounds for 
        the next notes anyway (delta 1 3 ...). """

    for chordPitch in chord.pitches:
        stepUp = chordPitch.transpose(1)
        stepDown = chordPitch.transpose(-1)
        if (note.name == stepDown.name or 
            note.name == stepDown.getEnharmonic().name or
            note.name == stepUp.name or
            note.name == stepUp.getEnharmonic().name):
                return True
    return False

def parseMelody(fullMeasureNotes, fullMeasureChords):

    """ Given the notes in a measure ('measure') and the chords in that measure
        ('chords'), generate a list (cluster) of abstract grammatical symbols to 
        represent that measure. Described in GTK's "Learning Jazz Grammars" (2009). 

        Inputs: 
        1) "measure" : a stream.Voice object where each element is a
            note.Note or note.Rest object.

                >>> m1
                <music21.stream.Voice 328482572>
                >>> m1[0]
                <music21.note.Rest rest>
                >>> m1[1]
                <music21.note.Note C>

            Can have instruments and other elements, removes them here.

        2) "chords" : a stream.Voice object where each element is a chord.Chord.

                >>> c1
                <music21.stream.Voice 328497548>
                >>> c1[0]
                <music21.chord.Chord E-4 G4 C4 B-3 G#2>
                >>> c1[1]
                <music21.chord.Chord B-3 F4 D4 A3>

            Can have instruments and other elements, removes them here. 

        Outputs:
        1) "fullGrammar" : a string that holds the abstract grammar for measure.

        Format: 
        (Remember, these are DURATIONS not offsets!)
        "R,0.125" : a rest element of  (1/32) length, or 1/8 quarter note. 
        "C,0.125<M-2,m-6>" : chord note of (1/32) length, generated
                             anywhere from minor 6th down to major 2nd down.
                             (interval <a,b> is not ordered). 
    """

    # Remove extraneous elements.x
    measure = copy.deepcopy(fullMeasureNotes)
    chords = copy.deepcopy(fullMeasureChords)
    measure.removeByNotOfClass([note.Note, note.Rest])
    chords.removeByNotOfClass([chord.Chord])

    # Information for the start of the measure.
    # 1) measureStartTime: the offset for measure's start, e.g. 476.0.
    # 2) measureStartOffset: how long from the measure start to the first element.
    measureStartTime = measure[0].offset - (measure[0].offset % 4)
    measureStartOffset  = measure[0].offset - measureStartTime

    """ Iterate over the notes and rests in measure, finding the grammar for each
        note in the measure and adding an abstract grammatical string for it. """

    fullGrammar = ""
    prevNote = None # Store previous note. Need for interval.
    numNonRests = 0 # Number of non-rest elements. Need for updating prevNote.
    for ix, nr in enumerate(measure):
        # Get the last chord. If no last chord, then (assuming chords is of length
        # >0) shift first chord in chords to the beginning of the measure.
        try: 
            lastChord = [n for n in chords if n.offset <= nr.offset][-1]
        except IndexError:
            chords[0].offset = measureStartTime
            lastChord = [n for n in chords if n.offset <= nr.offset][-1]

        # FIRST, get type of note, e.g. R for Rest, C for Chord, etc.
        # Dealing with solo notes here. If unexpected chord: still call 'C'.
        elementType = ' '
        # R: First, check if it's a rest. Clearly a rest --> only one possibility.
        if isinstance(nr, note.Rest):
            elementType = 'R'
        # C: Next, check to see if note pitch is in the last chord.
        elif nr.name in lastChord.pitchNames or isinstance(nr, chord.Chord):
            elementType = 'C'
        # L: (Complement tone) Skip this for now.
        # S: Check if it's a scale tone.
        elif isScaleTone(lastChord, nr):
            elementType = 'S'
        # A: Check if it's an approach tone, i.e. +-1 halfstep chord tone.
        elif isApproachTone(lastChord, nr):
            elementType = 'A'
        # X: Otherwise, it's an arbitrary tone. Generate random note.
        else:
            elementType = 'X'

        # SECOND, get the length for each element. e.g. 8th note = R8, but
        # to simplify things you'll use the direct num, e.g. R,0.125
        if (ix == (len(measure)-1)):
            # formula for a in "a - b": start of measure (e.g. 476) + 4
            diff = measureStartTime + 4.0 - nr.offset
        else:
            diff = measure[ix + 1].offset - nr.offset

        # Combine into the note info.
        noteInfo = "%s,%.3f" % (elementType, diff)

        # THIRD, get the deltas (max range up, max range down) based on where
        # the previous note was, +- minor 3. Skip rests (don't affect deltas).
        intervalInfo = ""
        if isinstance(nr, note.Note):
            numNonRests += 1
            if numNonRests == 1:
                prevNote = nr
            else:
                noteDist = interval.Interval(noteStart=prevNote, noteEnd=nr)
                noteDistUpper = interval.add([noteDist, "m3"])
                noteDistLower = interval.subtract([noteDist, "m3"])
                intervalInfo = ",<%s,%s>" % (noteDistUpper.directedName, 
                    noteDistLower.directedName)
                prevNote = nr

        # Return. Do lazy evaluation for real-time performance.
        grammarTerm = noteInfo + intervalInfo
        fullGrammar += (grammarTerm + " ")

    return fullGrammar.rstrip()


def unparseGrammar(grammar, measureChords):
    """ Given a grammar string and the measure chords, returns the generated
        notes for that measure. """
    print grammar, measureChords