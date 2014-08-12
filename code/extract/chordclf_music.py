""" Some functions for chordclf.py to use. """
from collections import defaultdict
import numpy as np
import re, itertools, random

# Convert music21 note to mingus note.
# This version (different from that in 3. Play Notes)
# doesn't return a Note object: returns a string.
def mingifytext(note):
    accidental = re.compile("[A-Z](-|#)[0-9]")
    if accidental.match(note):
        if '-' not in note: note = "%s%s-%s" % (note[0], note[1], note[2])
        else: note = note.replace('-', 'b-')
    else: note = "%s-%s" % (note[0], note[1])
    return note

# Given a MUSIC21 note, such as C5 or D#7, convert it
# into a note on the keyboard between 0 and 87 inclusive.
# Don't convert it for mingus; try to use music21 note style
# as much as possible for all this stuff.
def quantify(note):
    notevals = {
        'C' : 0,
        'D' : 2,
        'E' : 4,
        'F' : 5,
        'G' : 7,
        'A' : 9,
        'B' : 11
    }
    quantized = 0
    octave = int(note[-1]) - 1
    for i in note[:-1]:
        if i in notevals: quantized += notevals[i]
        if i == '-': quantized -= 1
        if i == '#': quantized += 1
    quantized += 12 * octave
    return quantized

# Extract notes in chords.
# Shorter single-note chords: lowest prob of being played
def getChords(allchords, mingify=True):
    chords_poss = []
    for chordname in allchords['FullName']:
        notenames = re.findall("[CDEFGAB]+[-]*[sharp|flat]*[in octave]*[1-9]", chordname)
        for ix in xrange(len(notenames)):
            notenames[ix] = notenames[ix].replace(" in octave ", '').replace("-sharp","#").replace("-flat","-")
        if mingify==True:
            notenames = [mingifytext(note) for note in notenames]
        else:
            notenames = [note for note in notenames]
        toDel = [ix for ix in xrange(len(notenames)) if "6" in notenames[ix] 
                 or "5" in notenames[ix]] # rm chords with notes too high, e.g. oct == 6 or 5
        notenames = [i for ix, i in enumerate(notenames) if ix not in toDel]
        if len(notenames) > 2: # min num of notes in valid chord = 3. Can change this
            chords_poss.append(sorted(notenames)) # important to sort, else can't find duplicates
    result = sorted(list(chords_poss for chords_poss,_ in itertools.groupby(chords_poss)))
    result = list(result for result,_ in itertools.groupby(result))
    return result

# Generates the altered scale from octaves 3 to 6 for a pitch (e.g. G-)
# for a given note (e.g. G-3) in music21 style.
# Returns altered scale as list of music21 notes.
def genAltered(note='C3'):
    # In case you have to convert a note (e.g. F#) into form below
    def convertSharps(note):
        pitch = ''.join([i for i in note if i.isdigit() is False])
        enharmonic = {"C#" : "D-", "D#" : "E-", "E#" : "F", "F#" : "G-", "G#" : "A-", "A#" : "B-", "B#" : "C"}
        if '#' in pitch: return enharmonic[pitch]
        return pitch
    
    # Get scale with dictionary. For example: allscales[note[:-1]]
    allscales = {
        "C"  : ["C3", "E-3", "F3", "G3", "B-3",
                "C4", "E-4", "F4", "G4", "B-4",
                "C5", "E-5", "F5", "G5", "B-5",
                "C6", "E-6", "F6", "G6", "B-6"],
        "D-" : ["D-3", "E3", "G-3", "A-3", "B3",
                "D-4", "E4", "G-4", "A-4", "B4",
                "D-5", "E5", "G-5", "A-5", "B5",
                "D-6", "E6", "G-6", "A-6", "B6"],
        "D"  : ["C3", "D3", "F3", "G3", "A3", 
                "C4", "D4", "F4", "G4", "A4", 
                "C5", "D5", "F5", "G5", "A5", 
                "C6", "D6", "F6", "G6", "A6"],
        "E-" : ["D-3", "E-3", "G-3", "A-3", "B-3",
                "D-4", "E-4", "G-4", "A-4", "B-4",
                "D-5", "E-5", "G-5", "A-5", "B-5",
                "D-6", "E-6", "G-6", "A-6", "B-6"],
        "E"  : ["D3", "E3", "G3", "A3", "B3",
                "D4", "E4", "G4", "A4", "B4",
                "D5", "E5", "G5", "A5", "B5",
                "D6", "E6", "G6", "A6", "B6"],
        "F"  : ["C3", "E-3", "F3", "A-3", "B-3",
                "C4", "E-4", "F4", "A-4", "B-4",
                "C5", "E-5", "F5", "A-5", "B-5",
                "C6", "E-6", "F6", "A-6", "B-6"],
        "G-" : ["D-3", "E3", "G-3", "A3", "B3",
                "D-4", "E4", "G-4", "A4", "B4",
                "D-5", "E5", "G-5", "A5", "B5",
                "D-6", "E6", "G-6", "A6", "B6"],
        "G"  : ["C3", "D3", "F3", "G3", "B-3",
                "C4", "D4", "F4", "G4", "B-4",
                "C5", "D5", "F5", "G5", "B-5",
                "C6", "D6", "F6", "G6", "B-6"],
        "A-" : ["D-3", "E-3", "G-3", "A-3", "B3",
                "D-4", "E-4", "G-4", "A-4", "B4",
                "D-5", "E-5", "G-5", "A-5", "B5",
                "D-6", "E-6", "G-6", "A-6", "B6"],
        "A"  : ["C3", "D3", "E3", "G3", "A3",
                "C4", "D4", "E4", "G4", "A4",
                "C5", "D5", "E5", "G5", "A5",
                "C6", "D6", "E6", "G6", "A6"],
        "B-" : ["D-3", "E-3", "F3", "A-3", "B-3",
                "D-4", "E-4", "F4", "A-4", "B-4",
                "D-5", "E-5", "F5", "A-5", "B-5",
                "D-6", "E-6", "F6", "A-6", "B-6"],
        "B"  : ["D3", "E3", "G-3", "A3", "B3",
                "D4", "E4", "G-4", "A4", "B4",
                "D5", "E5", "G-5", "A5", "B5",
                "D6", "E6", "G-6", "A6", "B6"]}
    pitch = ''.join([i for i in note if i.isdigit() is False])
    pitch = convertSharps(note) # Rm. octaveinfo, eg. G-5 --> G-, G5->G
    return allscales[pitch]

""" Hard-code altered scales right below for genChordNotes(). """

# Convert mingus note back to music21 note. WORKS
def unmingify(note):
    return note.replace('-','').replace('b','-')
    
# Given a list of mingus notes (i.e. a chord), say ['A-2', 'A-3', 'E-3'],
# Takes a chord (i.e. a list of notes) and returns a bitwise notevector with possible notes to go along with it.
# Idea: what if just generate notewise vector with exact same pitches? Indepedence assumption?
def genChordNotes(chord):
    chord = [unmingify(note) for note in chord] # really important to unmingify notes.
    notevect = np.zeros((1, 88))
    
    # populate with initial pitches
    for note in chord:
        notevect[0, quantify(note)] = 1
        
    # add initial pitches transposed to other octaves
    otheroctaves = range(3, 6)
    for note in chord:
        notebase = note[:-1]
        for octv in otheroctaves:
            put = bool(random.getrandbits(1)) # randomize other pitches
            if put is True:
                translated = "%s%s" % (notebase, octv)
                notevect[0, quantify(translated)] = 1
    
    # Add altered scale that contains most # of notes from chord notes
    # e.g. if chord = [e5, g5, b5] then want altered scale with as many of
    # those notes as possible. This lets you expand past simply
    # the notes already in that chord. Encode the notes of the altered
    # scale into the bitwise vector as with the initial pitches.
    # Maybe it works better w/o the altered scales; or maybe instead with pentatonics? try that.
    # Toggle below to include alternative notes (e.g. pentatonic/altered scales) or not
    altfreqs = defaultdict(int)
    for note in chord:
        for i in genAltered(note):
            altfreqs[i] += 1
    topnotes = [k for k, v in altfreqs.items() if v > 2] # get notes that overlap > 2 times
    for note in topnotes: # flip bits randomly from this list
        if bool(random.getrandbits(1)):
            notevect[0, quantify(note)] = 1
    
    # return the vector
    return notevect