#################################################################
# grammar.py
# Name: Evan Chow
# Description: generates a string representation of the measures
# in a melody stream.
#
##################################################################

from collections import OrderedDict, defaultdict
from itertools import groupby

def grammar(melody, accompaniment):
    """ Given a melody, generates a string representation of the abstract
    grammar for each measure as specified by KTG (2009). """

    # Group by measure with itertools. Assume 4/4 time.
    allMeasures = OrderedDict()
    offsetTuples = [(int(n.offset/4), n) for n in melody]
    for key, group in groupby(offsetTuples, lambda x: x[0]):
        # dictionary[i] = {note1, note2, note3 ...}
        allMeasures[key] = [n[1] for n in group]

    # Assert that everything turned out okay
    print "Testing ..."
    for measureNum, measureNoteList in allMeasures.items():
        print "Currently on measure %s: " % measureNum
        for i in measureNoteList:
            print i, "Offset: %s | Len: %s" % (i.offset, i.quarterLength)
        print
    print
    print

    # For each measure, find abstract string representation.
    grammarDict = OrderedDict() # grammarDict[measureNum] = ...
    # for measureNum, measureNoteList in allMeasures.items():
