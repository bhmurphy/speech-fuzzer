from pydub import AudioSegment
from pydub.generators import WhiteNoise
from sox import Transformer
from tempfile import NamedTemporaryFile, mktemp
from random import randint
from copy import copy
import parselmouth
from parselmouth.praat import call, run_file
from os import remove
from os.path import join, dirname, basename

# Most of this file either calls a pydub function or calls a sox
# function. Thank god for the open source community

def speedup(aud_seg, speed, **kwargs):
    """Speed up (or slow down) audio segment
    
    Args:
        aud_seg: audio segment to alter
        speed: new playback speed. Should be thought of as a
            percentage. For example, if we want to speed up
            aud_seg by 20%, we pass in 1.2. To slow it down
            to 80%, pass in 0.8
    """
    tfm = Transformer()
    tfm.tempo(speed)
    # Unfortunately, using our current libraries, idk how to make this faster
    # Sox requires an input file and an output file to perform the tempo shift
    temp_in_file = NamedTemporaryFile(suffix='.wav')
    aud_seg.export(temp_in_file, format='wav')
    temp_out_file = NamedTemporaryFile(suffix='.wav')
    tfm.build(temp_in_file.name, temp_out_file.name)

    return AudioSegment.from_file(temp_out_file.name, format='wav')

def add_noise(aud_seg, volume, **kwargs):
    """Add white noise of given volume to audio segment

    Args:
        aud_seg: audio segment to alter
        volume: volume of generated white noise in dBFS
            Note that this is a weird measurement
            where 0 is the max, the more negative
            the quieter it is
    """
    white_noise = WhiteNoise().to_audio_segment(duration=len(aud_seg), volume=volume)
    return aud_seg.overlay(white_noise)

def pitch_shift(aud_seg: AudioSegment, semi, **kwargs):
    """Pitch shift audio sample by semi semitones, without changing
    the speed of the audio segment.

    Arguments:
        aud_seg: audio segment to alter
        semi: Number of semitones to pitch audio
    """
    # Create a sox transformer
    tfm = Transformer()
    tfm.pitch(semi)
    # Unfortunately, using our current libraries, idk how to make this faster
    # Sox requires an input file and an output file to perform the pitch shift
    temp_in_file = NamedTemporaryFile(suffix='.wav')
    aud_seg.export(temp_in_file, format='wav')
    temp_out_file = NamedTemporaryFile(suffix='.wav')
    tfm.build(temp_in_file.name, temp_out_file.name)

    return AudioSegment.from_file(temp_out_file.name, format='wav')

def repeat_syllable(aud_seg, intervals=None, syllables=[0], repetitions=[4], **kwargs):
    """Repeat certain syllables certain numbers of times

    Args:
        aud_seg: audio segment to alter
        syllables: a list of which syllable numbers to repeat
        repetitions: a list determining how often to repeat each syllable.
            Must be the same length as syllables argument
    """
    # Temporarily save to file in order to run praat script on it
    temp_file = NamedTemporaryFile(suffix='.wav')
    aud_seg.export(temp_file, format='wav')
    # Get needed intervals in ms
    if not intervals:
        intervals = extract_syllable_intervals(dirname(temp_file.name), basename(temp_file.name))
    intervals = [intervals[i] for i in syllables]

    total_seg = aud_seg[0:intervals[0].start]
    audio_length = len(aud_seg)
    for i, syl in enumerate(intervals):
        for repeat in range(repetitions[i]):
            # Repeat sample repetitions times
            total_seg = total_seg.append(aud_seg[syl], crossfade=10)
            # Add a little spacing in between syllables
            total_seg = total_seg.append(AudioSegment.silent(duration=300), crossfade=10)
        next_start_or_end = _get_or_default(intervals, i+1, slice(audio_length, None))
        total_seg = total_seg.append(aud_seg[syl.stop: next_start_or_end.start], crossfade=10)
    
    return total_seg

def spacing(aud_seg_list, spaces, **kwargs):
    """Add space between list of audio segments and return a
    single audio segment

    Args:
        aud_seg_list: list of audio segments to be spliced
            together
        spaces: list that amount of space (in ms) to put
            between each sample. Should be the length
            of aud_seg_list - 1
    """
    # Create silent audio segments of spaces lengths
    silences = [AudioSegment.silent(duration=x) for x in spaces]
    # Only copying just in case a calling funciton makes the
    # assumption that the passed in list isn't changed
    total_seg = copy(aud_seg_list[0])
    # Append all audio samples with their given silences together
    for i, segment in enumerate(aud_seg_list[1:]):
        total_seg += silences[i]
        total_seg += segment
    return total_seg

def _get_or_default(iterable, n, default):
    """Get the nth index of an iterable, return a default if the nth value doesn't exist.

    Args:
        iterable: Iterable to pull value from
        n: Index to retrieve value from
        default: default value to return if the index is invalid
    """
    try:
        return iterable[n]
    except IndexError:
        return default

def extract_syllable_intervals(dir_name, file_name):
    """Get the ranges of each spoken syllable in an audio file

    See: Jadoul, Y., Thompson, B., & De Boer, B. (2018). Introducing
    Parselmouth: A Python interface to Praat. Journal of Phonetics, 71, 1-15.
    Page 18. Example is largely based off of the one given there.
    https://billdthompson.github.io/assets/output/Jadoul2018.pdf

    Args:
        dir_name: Name of directory file is located in
        file_name: Name of file to analyze
    """
    # Use Praat script to extract syllables
    objects = run_file('praat_scripts/syllable_nuclei.praat', -40, 2, 0.3, 0.1, True, dir_name, file_name)
    textgrid = objects[0]
    num = call(textgrid, "Get number of points", 1)
    # Get start times of every syllable
    syllable_nuclei = [call(textgrid, "Get time of point", 1, i + 1) for i in range(num)]

    syllable_intervals = []

    for i, start_time in enumerate(syllable_nuclei):
        # Retrieve the end of the syllable
        # This is either the start of the next syllable or the end of the
        # current interval
        interval = call(textgrid, "Get interval at time", 2, start_time)
        next_nucleus = _get_or_default(syllable_nuclei, i+1, float('inf'))
        interval_end = call(textgrid, "Get end time of interval", 2, interval)
        stop_time = min(next_nucleus, interval_end)

        # Convert  and stop time to milliseconds
        start_time = int(round(start_time * 1000))
        stop_time = int(round(stop_time * 1000))
        # Append a slice so we can easily slice the AudioSegment objects later
        syllable_intervals.append(slice(start_time, stop_time))
    # Remove generated .TextGrid file
    remove(join(dir_name, file_name + '.TextGrid'))
    return syllable_intervals

if __name__ == "__main__":
    # add these two lines to whatever main we agree on
    from logging import getLogger, ERROR
    getLogger('sox').setLevel(ERROR)
    aud = AudioSegment.from_file('tyler_weather_new.wav')

    repeat_syllable(aud).export('tyler_mutate.wav', format='wav')