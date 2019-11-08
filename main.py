import argparse
from os import listdir, mkdir
from os.path import isdir, join, abspath
from fuzzer import fuzz
from logging import getLogger, ERROR
getLogger('sox').setLevel(ERROR)


if __name__ == "__main__":
    # Creating the various arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', 
        help='Path to the source directory where seeds are stored', default='seeds')
    parser.add_argument('-o', '--output', 
        help='Path to the output directory where results will be stored', default='results')
    parser.add_argument('-n', '--num', type=int, default=100,
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
    seeds_files = {}
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
        else:
            seeds_files[filename] = [join(abspath(args.source), filename, seed) for seed in listdir(join(args.source, filename))]
    
    if not isdir(args.output):
        try:
            mkdir(args.output)
        except OSError:
            print("Creation of output directory '{}' failed".format(args.output))
            exit(1)
    
    print("Number of iterations = {}".format(args.num))
    for i in range(args.num):    
        for key in seeds_files.keys():
            #print(key, seeds_files[key])
            fuzz(key, seeds_files[key])


