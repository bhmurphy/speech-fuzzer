import effects_processor
from random import choice, random, randrange, uniform, sample
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
from os.path import join, dirname, basename
from Failure import Failure
from tqdm import tqdm

PHRASE_MUTATOR_CHANCE = 0.35
WORD_MUTATOR_CHANCE = 0.5
SPACING_CHANCE = 0.9
ONE_REPETITION_CHANCE = 0.8

def speedup(segment):
    speed = uniform(0.5, 1.8)
    # print("Speed UP {}%".format(speed))
    return effects_processor.speedup(segment, speed), 'Speed Up', speed

def add_noise(segment):
    volume = uniform(-75, -50)
    # print("Add Noise ", volume)
    return effects_processor.add_noise(segment, volume), 'Add White Noise', volume

def pitch_shift(segment):
    pitch = uniform(-12,12)
    # print("Pitch Shift ", pitch)
    return effects_processor.pitch_shift(segment, pitch), 'Pitch Shift', pitch

def spacing(segments):
    # 50% chance to have same spacing between words
    if random() > 0.5:
        # Same spacing
        space = uniform(25, 500)
        spaces = [space for x in range(len(segments) - 1)]
    else:
        # Different spacing
        spaces = [uniform(50, 500) for x in range(len(segments) - 1)]
    # return effects_processor.spacing()
    return effects_processor.spacing(segments, spaces), 'Spacing', spaces

def repeat_syllable(segment):
    # praat script requires a file on disk
    temp_file = NamedTemporaryFile(suffix='.wav')
    segment.export(temp_file, format='wav')
    intervals = effects_processor.extract_syllable_intervals(\
        dirname(temp_file.name), basename(temp_file.name))
    num_interv = len(intervals)
    # If the praat script fails to find any syllable intervals, return
    # the unchanged audio segment
    if num_interv == 0:
        return segment, 'Repeat Syllable', None
    # Otherwise, select parameters randomly
    # Number of syllables to repeat
    val = random()
    num_syll = 1 if val < ONE_REPETITION_CHANCE else randrange(1, num_interv + 1)
    # Which syllables to repeat
    syllables = sorted(sample(range(num_interv), num_syll))
    # How often to repeat each syllable
    repetitions = sample(range(2, 7), num_syll)
    return effects_processor.repeat_syllable(segment, intervals, syllables, repetitions),\
         'Repeat Syllable', {'Repeated Syllables': syllables, 'Repetitions': repetitions}

def change_volume(segment):
    dB = uniform(5, 15)
    if random() > 0.5:
        dB *= -1
    return effects_processor.change_volume(segment, dB), 'Change Volume', dB

def fuzz_phrase(files, passed_path, failed_path, fail_accumulator, client):
    # Put all relevant functions in a list
    possible_mutators = [pitch_shift, speedup, add_noise, repeat_syllable]
    for filename in tqdm(files, desc="Phrase", ascii=True, leave=False):
        initial_user, initial_google = client.get_responses(filename)
        segment = AudioSegment.from_file(filename)
        val = 0
        mutators = []
        args = []
        while val <= PHRASE_MUTATOR_CHANCE:
            # Do a random choice 
            mutation = choice(possible_mutators)
            # Perform the mutations
            segment, this_mut, this_arg = mutation(segment)
            mutators.append(this_mut)
            args.append(this_arg)
            # Repeat? 
            val = random()
        temp_file = NamedTemporaryFile(suffix='.wav')
        segment.export(temp_file.name, format='wav')
        mutated_user, mutated_google = client.get_responses(temp_file.name)
        file_path = '{}_{}.wav'.format(filename.split('/')[-1].rstrip('.wav'), segment.__hash__())
        if mutated_user == initial_user:
            # The mutator did not change googles understanding
            segment.export(join(passed_path, file_path), format='wav')
        else:
            # The mutator did change googles understanding
            this_fail = Failure(file_path, mutators, args, client.get_similarity(initial_user, mutated_user), \
                client.get_similarity(initial_google, mutated_google))
            fail_accumulator.addFailure(this_fail)
            segment.export(join(failed_path, file_path), format='wav')
        fail_accumulator.total_runs+=1

def fuzz_word(pairings, passed_path, failed_path, fail_accumulator, client):
    possible_mutators = [pitch_shift, speedup, repeat_syllable, add_noise, change_volume]
    for seed_string, source in tqdm(pairings, desc="Word", ascii=True, leave=False):
        combined_audio = AudioSegment.empty()
        segments = []
        # Collect audio segments and build unmodified audio sample
        #print("'{}'".format(seed_string))
        for word in seed_string.split():
            current = AudioSegment.from_file(join(source, word + '.wav'))
            segments.append(current)
            combined_audio += current
        # Create temporary file to send to google
        temp_file = NamedTemporaryFile(suffix='.wav')
        combined_audio.export(temp_file.name, format='wav')
        initial_user, initial_google = client.get_responses(temp_file.name)
        val = 0.0
        mutators = []
        args = []
        while val < WORD_MUTATOR_CHANCE:
            index = randrange(len(segments))
            mutation = choice(possible_mutators)
            segments[index], this_mut, this_arg = mutation(segments[index])
            mutators.append(this_mut)
            args.append(this_arg)
            val = random()
        # Decide if we should manipulate the spacing
        val = random()
        if val < SPACING_CHANCE:
            spacing(segments)
        combined_audio = AudioSegment.empty()
        for seg in segments:
            combined_audio += seg
        temp_file = NamedTemporaryFile(suffix='.wav')
        combined_audio.export(temp_file.name, format='wav')
        mutated_user, mutated_google = client.get_responses(temp_file.name)
        file_path = '{}_{}.wav'.format(seed_string.replace(" ", "_"), combined_audio.__hash__())
        
        if mutated_user == initial_user and initial_user is not None and mutated_user is not None:
            # The mutator did not change googles understanding
            combined_audio.export(join(passed_path, file_path), format='wav')
        else:
            # The mutator did change googles understanding
            this_fail = Failure(file_path, mutators, args, client.get_similarity(initial_user, mutated_user), \
                client.get_similarity(initial_google, mutated_google))
            fail_accumulator.addFailure(this_fail)
            combined_audio.export(join(failed_path, file_path), format='wav')
        fail_accumulator.total_runs+=1

        