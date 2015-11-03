"""
The end goal for this file is to be able to parse a JSON array of
beats in a song, and output a MIDI file that matches the specification.

For now, all we're trying to do is create a MIDI representation of the beat
sequencing in recover.json. We want to see what the MIDI output even sounds like and
to try to experiment different ways of adjusting the pitch, since the current dataset
only gives us enough information for time and duration of the beats, not the pitches.
"""

import midi
import json

# This is how long in ticks a quarter note is, I think.
ONE_BEAT_IN_TICKS = 220

class Track:
    def __init__(self):
        self.pattern = midi.Pattern()
        self.track = midi.Track()
        self.pattern.append(self.track)

    def __str__(self):
        return str(self.pattern)

    def note(self, length, pitch):
        self.track.append(midi.NoteOnEvent(tick=0, velocity=50, pitch=pitch))
        self.track.append(midi.NoteOffEvent(tick=length, pitch=pitch))

    def finish(self, filename):
        # "All Notes End" event
        self.track.append(midi.ControlChangeEvent(tick=0, control=123))
        self.track.append(midi.EndOfTrackEvent(tick=1))
        midi.write_midifile(filename, self.pattern)


class ENAnalysis:
    def __init__(self, filename):
        f = open(filename, "r")
        d = f.read().replace('\n', '')
        f.close()
        self.__dict__ = json.loads(d)

    def __str__(self):
        return str(self.data)


if __name__ == "__main__":
    ## Example of making a MIDI track
    #track = Track()
    ## We could make a full bar here instead by repeating this 3 more times
    #track.note(ONE_BEAT_IN_TICKS, midi.C_3)
    #track.finish("output.mid")
    #print track

    analysis = ENAnalysis("recover.json")
    first_bar = analysis.bars[0]
    first_beat = analysis.beats[0]
    """
    Okay, here's where it gets fucking fun.
    Since we don't want to actually care about milliseconds, we want to convert Echo Nest's
    model of a "bar", into ours.
    A bar is composed of multiple beats, where the start of the bar will match the start
    of a beat and the result of (start + duration) will match the value of (start + duration)
    for another one of the beat objects in the list.
    That means given a list of beats and a list of bars, we can associate which beats are in which
    bars.
    After doing this, we can create our own version of bars which instead of being composed of
    beats that have start and durations, will be composed of beats that have a start and end time relative
    to the overall length of the bar.
    Given those, instead of having to figure out how long a 0.165s duration beat is, we can just say "Oh well
    it's going to take 1/4 of the bar, so make it ONE_BEAT_IN_TICKS (a quarter note)" -- Awesome, right?
    """
    