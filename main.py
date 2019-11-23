import argparse
from os import listdir, mkdir
from os.path import isdir, join, abspath
from fuzzer import fuzz_phrase, fuzz_word
from logging import getLogger, ERROR
from ttsHandler import handleTextSeeds, processPhrases
from json import load
from FailureAllocator import FailureAllocator
from tqdm import trange

getLogger('sox').setLevel(ERROR)

def addSeedFiles(dict_to_extend, source_path, seed_type):
    if seed_type == "phrase":
        dict_to_extend['phrase'].extend([join(source_path, seed) for seed in listdir(source_path)])
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
                    for seed_string in processPhrases(data['words'].values()):
                        string_list.append((seed_string.rstrip(), source_path))


if __name__ == "__main__":
    # Creating the various arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', 
        help='Path to the source directory where seeds are stored', default='seeds')
    parser.add_argument('-o', '--output', 
        help='Path to the output directory where results will be stored', default='results')
    parser.add_argument('-n', '--num', type=int, default=5,
        help='The number of iterations you want to run for each type. Default = 100')
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

    print("Number of iterations = {}".format(args.num))
    fail_allocator = FailureAllocator(args.output)
    for i in trange(args.num, desc="Iterations", ascii=True, leave=False):    
        if len(seeds_files['phrase']) > 0:
            fuzz_phrase(seeds_files['phrase'], pass_path, failed_path, fail_allocator)
        if len(seeds_files['word']) > 0:
            fuzz_word(seeds_files['word'], pass_path, failed_path, fail_allocator)
    fail_allocator.writeFailures()

    




