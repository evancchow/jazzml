""" The master client file. Given your well-structured modules in the
    relative subfolders, this Python script from start to finish
    simulates jazz improvisation. """

# Imports
import sys
sys.path.append('./code/extract/')
from parseraw import parseRawFile

# Parse the MIDI data.
filename = './Oscar-Peterson-2.mid'
metronomeNum, timeSig, allChords, allNotes = parseRawFile(filename)

# Write out notes to a text file. 
# Ideally, you'll be able to keep everything
# in RAM eventually, so no need for intermediate text files.
with open('oscar2notes.txt', 'wb') as f:
    f.write("%s\n" % metronomeNum)
    f.write("%s\n" % timeSig)
    f.write("Note/Rest,Octave,Len,Offset\n")
    for i in allNotes:
        f.write("%s,%s,%s,%s\n" % (i.name, 
            i.octave, i.quarterLength, float(i.offset)))

# Write out chords to a text file.
with open('oscar2chords.txt', 'wb') as f:
    f.write("%s\n" % metronomeNum)
    f.write("%s\n" % timeSig)
    f.write("FullName,CommonName,Len,Offset\n")
    for i in allChords:
        f.write("%s,%s,%s,%s\n" % (i.fullName,
            i.pitchedCommonName, i.quarterLength, float(i.offset)))
