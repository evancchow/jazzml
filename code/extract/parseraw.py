""" This a module to parse the raw MIDI data, and get its information. 
    Test the functions in here by running oscar2.py and seeing if the
    musical information can still be written out. """

from music21 import *

def parseRawFile(filename):
    """ Given a raw file name (string), parse it. Return:
        1) The metronome number
        2) The time signature
        3) List of all the chords
        4) List of all the notes 

        // TODO: Make this recursive so it finds all chords and notes. """

    # Get the musical information.
    oscar2 = converter.parse(filename)
    singlepart = oscar2[0]
    timesig = singlepart.getElementsByClass(meter.TimeSignature)[0]
    mmark = singlepart.getElementsByClass(tempo.MetronomeMark)[0]
    allnotes = []
    allchords = []
    for ix, voice in enumerate(singlepart.getElementsByClass(stream.Voice)):
        notes = voice.getElementsByClass(note.Note).notes
        chords = voice.getElementsByClass(chord.Chord)
        for i in notes:
            allnotes.append(i)
        for i in chords:
            allchords.append(i)

    # Return (1), (2), (3), and (4).
    timesig = "%s / %s" % (timesig.numerator, timesig.denominator)
    return mmark.number, timesig, allchords, allnotes







