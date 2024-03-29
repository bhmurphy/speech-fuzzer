import argparse
from os import listdir, mkdir, remove
from os.path import isdir, join, isfile
from fuzzer import fuzz_phrase, fuzz_word
from logging import getLogger, ERROR
from ttsHandler import handleTextSeeds, processPhrases
from json import load
from FailureAccumulator import FailureAccumulator
from tqdm import trange
from generators import generate_words_tts
from GoogleClient import GoogleClient

getLogger('sox').setLevel(ERROR)

def addSeedFiles(dict_to_extend, source_path, seed_type):
    if seed_type == "phrase":
        dict_to_extend['phrase'].extend([join(source_path, seed) for seed in listdir(source_path) if seed!='.DS_Store'])
    elif seed_type == 'text_word':
        with open(join(source_path, 'seed_guide.txt')) as guide:
            string_list = dict_to_extend['word'] 
            for line in guide:
                string_list.append((line.rstrip(), source_path))
    else:
        string_list = dict_to_extend['word']
        for filename in listdir(source_path):
            if filename.endswith('.json'): 
                with open(join(source_path, filename), 'r') as guide_file:
                    data = load(guide_file)
                    # for seed_string in processPhrases(data['words'].values()):
                    for key, value in data['words'].items():
                        for seed_string in processPhrases([value]):
                            string_list.append((seed_string.rstrip(), join(source_path, key)))

def check_word_seeds(word_seeds):
    """When running in word mode, check if the corresponding word files actually exist
        args: word_seeds: list of (phrase_str, directory) tuples from the 'word' key of the
            seeds_files dictionary
    """
    pos_responses = ['y', 'yes']
    neg_responses = ['n', 'no']
    for seed, directory in word_seeds:
        to_generate = []
        for word in seed.split():
            word_file = join(directory, word + '.wav')
            if not isfile(word_file):
                gen_response = input('Seed file {} does not exist. Generate it using text-to-speech? (n to exit)\
                    [y/n] '.format(word_file))
                # Only accept a valid response
                while gen_response not in (pos_responses + neg_responses):
                    gen_response = input('Only accepted responses are y or n. Generate file using text-to-speech?\
                        (n to exit) [y/n] ')
                if gen_response.lower() in pos_responses:
                    to_generate.append(word)
                else: # response is "no"
                    print("Exiting...")
                    quit()
        # Only call the function if we have any words to generate
        if len(to_generate) > 0:
            generate_words_tts(to_generate, directory)

if __name__ == "__main__":
    # Creating the various arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', 
        help='Path to the source directory where seeds are stored', default='seeds')
    parser.add_argument('-o', '--output', 
        help='Path to the output directory where results will be stored', default='results')
    parser.add_argument('-n', '--num', type=int, default=5,
        help='The number of iterations you want to run for each type. Default = 5')
    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument('-i', '--ignore', choices=['text', 'word', 'phrase'],  
        help="The type of seeds you want to ignore")
    exclusive.add_argument('-t', '--type', choices=['text', 'word', 'phrase'],  
        help="The one type of seed you want to use")
    args = parser.parse_args()

    print("Speech Fuzzer v0.1")
    # Checking to see if a valid directory was given
    try:
        files = listdir(args.source)
    except FileNotFoundError:
        print("Directory: '{}' not found".format(args.source))
        exit(1)
    except NotADirectoryError:
        print("'{}' is a file not directory".format(args.source))
        exit(1)
    # Checking the contents of the directory
    expected_folders = ['text', 'word', 'phrase']
    seeds_files = {'phrase': [], 'word': []}
    if args.ignore is not None:
        expected_folders.remove(args.ignore)
    if args.type is not None:
        expected_folders = [args.type]
    for filename in expected_folders:
        if filename not in files:
            print("Expected directory '{}' not found in source directory '{}'".format(filename, args.source))
            exit(1)
        elif not isdir(join(args.source, filename)):
            print("'{}' in source directory '{}' should be directory not file".format(filename, args.source))
            exit(1)
        elif filename == 'text':
            # Generate the seeds with text-to-speech
            handleTextSeeds(join(args.source, filename))
            # Create paths to seed directories
            phrase_source = join(args.source, filename, 'phrase')
            word_source = join(args.source, filename, 'word')
            # Add the new seeds for processing
            addSeedFiles(seeds_files, phrase_source, 'phrase')
            addSeedFiles(seeds_files, word_source, 'text_word')
        else:
            # Create path to seed 
            seeds_source = join(args.source, filename)
            #Add the new seeds for processing
            addSeedFiles(seeds_files, seeds_source, filename)
    # Check if the output directory exists or is directory
    # If not create it  
    pass_path = join(args.output, 'passed')
    failed_path = join(args.output, 'failed')
    if not isdir(args.output):
        try:
            mkdir(args.output)
            mkdir(failed_path)
            mkdir(pass_path)
        except OSError:
            print("Creation of output directory '{}' failed".format(args.output))
            exit(1)
    # If it does exist check to see if their are passed and failed subdirectories
    # If not create them
    else:
        files = listdir(args.output)
        if 'passed' not in files:
            try:
                mkdir(pass_path)
            except OSError:
                print("Creation of output sub directory '{}' failed".format(pass_path))
                # exit(1)
        if 'failed' not in files:
            try:
                mkdir(failed_path)
            except OSError:
                print("Creation of output sub directory '{}' failed".format(failed_path))
                # exit(1)

    if 'word' in seeds_files:
        check_word_seeds(seeds_files['word'])

    print("Number of iterations = {}".format(args.num))
    fail_accumulator = FailureAccumulator(args.output)
    client = GoogleClient()
    try:
        for i in trange(args.num, desc="Iterations", ascii=True, leave=False):    
            if len(seeds_files['phrase']) > 0:
                fuzz_phrase(seeds_files['phrase'], pass_path, failed_path, fail_accumulator, client)
            if len(seeds_files['word']) > 0:
                fuzz_word(seeds_files['word'], pass_path, failed_path, fail_accumulator, client)
    except KeyboardInterrupt:
        print("\n\nStopped early by user. Writing results file...")
        if isfile('tmp.wav'):
            remove('tmp.wav')
    fail_accumulator.writeFailures()
