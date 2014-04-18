""" Pymidi test for manipulating MIDI files.
    For a midi file (imported), element:
    [0], TrackNameEvent. The track info.
    [1], TextMetaEvent. Author info.
    [2], CopyrightMetaEvent. Copyright info.
    [3], CopyrightMetaEvent. More copyright info.
    [4], TextMetaEvent. How file was created.
    """

from music21 import *

fp = './example.mid'
streamScore = midi.translate.midiFilePathToStream(fp)