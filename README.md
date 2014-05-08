JAZZML: Statistical Jazz Improvisation
======

Final project for COS 401: Introduction to Machine Translation. Computer jazz improvisation powered by machine learning,
specifically trigram modeling, K-Means clustering, and chord inference with SVMs.

Messy code + needs to be better modularized.

Dependencies:
NumPy
SciPy
Pandas
Scikit-Learn
MatPlotLib

In addition, you'll need a couple of specialized music libraries for Python:

music21 - for MIDI data extraction
mingus (https://code.google.com/p/mingus/) - for playback
fluidsynth - for playback

----------

If you're new here: Included is a sample MIDI file (Oscar-Peterson-2.mid) for analysis and generation. For a quick demo, go to the subdirectory "./oscar/oscar2" and run things in this order (assuming you have the dependencies):

First, run the script oscar2.py as:

$ python oscar2.py > oscar2chords.txt
(or $ python oscar2.py > oscar2notes.txt based on stdin)

This should give you two data files which represent the chords and the notes encoded in the original MIDI file: oscar2chords.txt, and oscar2notes.txt.

Next, to generate new notes with the N-Gram model, run iPython notebook 6a: The N-Gram Pipeline, Part I which writes out the n-grams to the file oscar2ngrams.txt.

Next, to generate the chord classifier (SVM) with chord notes, first run iPython notebook 5: Extract Chords to process the raw data in oscar2chords.txt, clean it up, and write it out to oscar2chords_extract.txt. Then run iPython notebook 7: Predictive Chord Modeling with Bitwise Note Vectors, which reads in that just-created file, trains an SVM to return those chords based on consonant pentatonic notes (semirandomly generated), and cPickles that SVM to disk.

Finally, for chord accompaniment and dynamic playback, run notebook 6b: The N-Gram Pipeline, Part II.
