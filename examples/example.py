""" Take in example.mid and rewrite for use with scipy
    sparse matrix. Example of how to parse MIDI with Music21.
    Execution: python parse.py [file to print to] """

from music21 import *
example = converter.parse('example.mid')
data = example.parts[0]
# data.show()

print "%s,%s,%s,%s" % ("Note/Rest", "Octave", "Len","Offset")
notes = [i for i in data.notesAndRests]
for n in notes:
    if isinstance(n, note.Note):
        # alternative n.pitch.nameWithOctave
        print "%s,%s,%s,%s" % (str(n.pitch.name), n.pitch.octave, n.quarterLength, n.offset)
    elif isinstance(n, note.Rest):
        print "%s,%s,%s,%s" % ("Rest", None, n.quarterLength, n.offset)