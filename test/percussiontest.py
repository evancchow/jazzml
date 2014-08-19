""" Test playing percussion with fluidsynth path. """

from music21 import *
import time, fluidsynth


play = lambda x: midi.realtime.StreamPlayer(x).play()
stop = lambda: pygame.mixer.music.stop()

# Get music.
metheny = converter.parse("../andtheniknew_metheny.mid")

# Start fluidsynth.
fs = fluidsynth.Synth()
fs.start()
sfid = fs.sfload("./darbuka.sf2")
fs.program_select(0,sfid,0,0)

tempo = 150.0

melodyStream = metheny[5]
melody, melody2 = melodyStream.getElementsByClass(stream.Voice)
for j in melody2:
    melody.insert(j.offset, j)






