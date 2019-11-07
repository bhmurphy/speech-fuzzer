import effects_processor
import generators

def speedup(filename):
    args = []
    effects_processor.speedup()

def add_noise(filename):
    args = []
    effects_processor.add_noise()

def pitch_shift(filename):
    args = []
    effects_processor.pitch_shift()

def spacing(filenames):
    args = []
    effects_processor.spacing()


def fuzz(data_type, files):
    # Put all relevant functions in a list
    possible_mutators = [speedup, add_noise, pitch_shift]
    if data_type == 'word':
        possible_mutators.append(spacing)
    
    # Do a random choice 

    # Perform the mutations

    # Repeat? 

    # 