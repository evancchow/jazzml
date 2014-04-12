""" Example of parsing the Alice midi file.

    Structure:

    --> Score
    -----> Part (alice[0])
    --------> instrument.Piano
    --------> tempo.MetronomeMark
    --------> key.KeySignature
    --------> meter.TimeSignature
    --------> stream.Voice
    --------> stream.Voice
    --------> stream.Voice
    --------> stream.Voice
    --------> stream.Voice
    --------> stream.Voice
    --------> stream.Voice

    Each voice has notes in it. 

    Voice
    ----> stream
    --------> notes

    e.g. To access all the notes in the first voice:

    notes = alice[0].getElementsByClass(stream.Voice)[0]
    .getElementsByClass(note.Note).notes
    
    For use with Pandas; still need to sort by the
    column for offset. Skip first 2 rows for the
    metronome mark and time signature. """    

from music21 import *

alice = converter.parse('./alice.mid')
singlepart = alice[0]
allnotes = []
timesig = alice[0].getElementsByClass(meter.TimeSignature)[0]
mmark = alice[0].getElementsByClass(tempo.MetronomeMark)[0]
print mmark.number
print "%s / %s" % (timesig.numerator, timesig.denominator)
print "Note/Rest,Octave,Len,Offset"
for voice in singlepart.getElementsByClass(stream.Voice):
    notes = voice.getElementsByClass(note.Note).notes
    for i in notes:
        print "%s,%s,%s,%s" % (i.name, i.octave,
            i.quarterLength, float(i.offset))