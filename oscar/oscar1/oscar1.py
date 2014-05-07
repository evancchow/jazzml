""" Extract note and chord information from oscar MIDI #1. """
""" Structure for Oscar-Peterson-2.mid:
	
	Score
		Part
			MetronomeMark
			TimeSignature
			Voice
			Voice
			Voice
			Voice
			Voice
			Voice
			Voice
			Voice
			Piano
															"""

from music21 import *

oscar2 = converter.parse('./Oscar-Peterson-1.mid')

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

print mmark.number
print "%s / %s" % (timesig.numerator, timesig.denominator)

# toggle with printing out chords below > oscar2notes.txt
# print "Note/Rest,Octave,Len,Offset"
# for i in allnotes:
#     print "%s,%s,%s,%s" % (i.name, i.octave, i.quarterLength, float(i.offset))

# toggle with printing out notes above > oscar2chords.txt
print "FullName,CommonName,Len,Offset"
for i in allchords:
    print "%s,%s,%s,%s" % (i.fullName, 
      i.pitchedCommonName, i.quarterLength, float(i.offset))