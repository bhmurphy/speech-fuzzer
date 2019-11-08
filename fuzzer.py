import effects_processor
import generators
from random import choice, random, randrange, uniform
import subprocess
import re
from pydub import AudioSegment
from tempfile import NamedTemporaryFile

def speedup(segment):
    speed = uniform(0.5, 1.5)
    print("Speed UP {}%".format(speed))
    return effects_processor.speedup(segment, speed)

def add_noise(segment):
    print("Add Noise")
    volume = uniform(-75, -50)
    return effects_processor.add_noise(segment, volume)

def pitch_shift(segment):
    pitch = float(randrange(-12,12))
    print("Pitch Shift ", pitch)
    return effects_processor.pitch_shift(segment, pitch)

def spacing(segment):
    args = []
    return effects_processor.spacing()

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

def fuzz(data_type, files):
    # Put all relevant functions in a list
    possible_mutators = [speedup]
    if data_type == 'word':
        possible_mutators.append(spacing)
    for filename in files:
        initial_user, initial_google = get_responses(filename)
        segment = AudioSegment.from_file(filename, format='wav')
        val = 0
        while val <= 0.15:
            # Do a random choice 
            mutation = choice(possible_mutators)
            # Perform the mutations
            segment = mutation(segment)
            # Repeat? 
            val = random()
        temp_file = NamedTemporaryFile(suffix='.wav')
        segment.export(temp_file.name, format='wav')
        segment.export('mutated.wav', format='wav')
        mutated_user, mutated_google = get_responses(temp_file.name)
        if mutated_user == initial_user:
            # The mutator did not do anything thus not interesting
            print('match')
        else:
            #There is a difference so it is interesting
            print('did not match. "{}" vs "{}"'.format(initial_user, mutated_user))
            #print(initial_google, mutated_google)