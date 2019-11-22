import effects_processor
import generators
from random import choice, random, randrange, uniform
import subprocess
import re
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
from os.path import join

def speedup(segment):
    speed = uniform(0.5, 1.8)
    print("Speed UP {}%".format(speed))
    return effects_processor.speedup(segment, speed)

def add_noise(segment):
    volume = uniform(-75, -50)
    print("Add Noise ", volume)
    return effects_processor.add_noise(segment, volume)

def pitch_shift(segment):
    pitch = float(randrange(-12,12))
    print("Pitch Shift ", pitch)
    return effects_processor.pitch_shift(segment, pitch)

def spacing(segment):
    args = []
    return effects_processor.spacing()

def repeat_syllable(segment):
    pass

def get_responses(filename):
    process = subprocess.Popen(['googlesamples-assistant-pushtotalk', 
            '--project-id', 'fuzzing-personal-assistants ',
            '--device-model-id', 'fuzzing-personal-assistants-tylers-pc ',
            '-i', filename,
            '-o', 'tmp.wav', '-v'], stderr=subprocess.PIPE)
    val = 0
    output = process.communicate()[1].decode('utf-8')
    #print(output)
    user_matches = re.findall("Transcript of user request: \"(.*?)\"", str(output))
    google_match = re.findall("supplemental_display_text: \"(.*?)\"", str(output))
    user_final_match = None
    if len(user_matches) > 0:
        user_final_match = user_matches[-1]
    #print(user_matches, google_match)
    google_final_match = None
    if len(google_match) > 0:
        google_final_match = google_match[0]
    return user_final_match, google_final_match

def fuzz_phrase(files):
    # Put all relevant functions in a list
    possible_mutators = [pitch_shift, speedup, repeat_syllable, add_noise]
    for filename in files:
        initial_user, initial_google = get_responses(filename)
        segment = AudioSegment.from_file(filename, format='wav')
        val = 0
        while val <= 0.5:
            # Do a random choice 
            mutation = choice(possible_mutators)
            # Perform the mutations
            segment = mutation(segment)
            # Repeat? 
            val = random()
        temp_file = NamedTemporaryFile(suffix='.wav')
        segment.export(temp_file.name, format='wav')
        # FOR TESTING remove when finished
        segment.export('mutated.wav', format='wav')
        mutated_user, mutated_google = get_responses(temp_file.name)
        if mutated_user == initial_user:
            # The mutator did not do anything thus not interesting
            print('match')
        else:
            #There is a difference so it is interesting
            print('did not match. "{}" vs "{}"'.format(initial_user, mutated_user))
            #print(initial_google, mutated_google)

def fuzz_word(pairings):
    for seed_string, source in pairings:
        possible_mutators = [pitch_shift, speedup, repeat_syllable, add_noise, spacing]
        raw_audio = AudioSegment.empty()
        segments = []
        # Collect audio segments and build unmodified audio sample
        print(seed_string)
        for word in seed_string.split():
            current = AudioSegment.from_file(join(source, word + '.wav'))
            segments.append(current)
            raw_audio += current
        # Create temporary file to send to google
        temp_file = NamedTemporaryFile(suffix='.wav')
        raw_audio.export(temp_file.name, format='wav')
        # FOR TESTING remove when finished 
        raw_audio.export('raw_{}.wav'.format(seed_string.replace(" ", "_")), format='wav')
        initial_user, initial_google = get_responses(temp_file.name)
        print(initial_user, initial_google)
