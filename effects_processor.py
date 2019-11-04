from pydub import AudioSegment
from pydub import effects
from pydub.generators import WhiteNoise
from sox import Transformer
from tempfile import NamedTemporaryFile, mktemp
from random import randint
from copy import copy
from generators import generate_words_tts

# Most of this file either calls a pydub function or calls a sox
# function. Thank god for the open source community

def speedup(aud_seg: AudioSegment, speed: float, **kwargs):
    """Speed up (or slow down) audio segment
    
    Arguments:
    aud_seg -- audio segment to alter
    speed -- new playback speed. Should be thought of as a
             percentage. For example, if we want to speed up
             aud_seg by 20%, we pass in 1.2. To slow it down
             to 80%, pass in 0.8
    """
    return effects.speedup(aud_seg, playback_speed=speed)

def add_noise(aud_seg: AudioSegment, volume: float, **kwargs):
    """Add white noise of given volume to audio segment

    Arguments:
    aud_seg -- audio segment to alter
    volume -- volume of generated white noise in dBFS
              Note that this is a weird measurement
              where 0 is the max, the more negative
              the quieter it is
    """
    white_noise = WhiteNoise().to_audio_segment(duration=len(aud_seg), volume=volume)
    return aud_seg.overlay(white_noise)

def pitch_shift(aud_seg: AudioSegment, semi: float, **kwargs):
    """Pitch shift audio sample by semi semitones, without changing
    the speed of the audio segment.

    Arguments:
    aud_seg -- audio segment to alter
    semi -- Number of semitones to pitch audio
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

def spacing(aud_seg_list: list, spaces: list, **kwargs):
    """Add space between list of audio segments and return a
    single audio segment

    Arguments:
    aud_seg_list --- list of audio segments to be spliced
                     together
    spaces --- list that amount of space (in ms) to put
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
        print(len(silences))
        total_seg += silences[i]
        total_seg += segment
    return total_seg

if __name__ == "__main__":
    # add these two lines to whatever main we agree on
    from logging import getLogger, ERROR
    getLogger('sox').setLevel(ERROR)