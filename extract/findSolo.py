""" Given a fullStream (e.g. the melody and accompaniment in one
    stream), finds where the solo starts and uses the method
    stream.getElementsByOffset(offsetStart, offsetEnd) to find out
    where the solo starts and update the full stream accordingly. """

from music21 import *
import sys, copy

def findSolo(fullStream):
    soloStream = copy.deepcopy(fullStream)






    # Return the modified stream
    return soloStream