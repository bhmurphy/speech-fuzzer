import json
from os import listdir, mkdir
from os.path import join,abspath, isdir
import generators

def processPhrases(raw_phrase_values):
    strings = []
    for phrase in raw_phrase_values:
        if len(phrase) == 1:
            strings.append(phrase[0])
        else:
            synonyms = []
            string = ""
            for i in range(len(phrase)):
                if isinstance(phrase[i], list):
                    synonyms.extend(phrase[i])
                    string += "{} "
                else:
                    string += phrase[i] + " "
            for i, syn in enumerate(synonyms):
                strings.append(string.format(syn))
    return strings


def handleTextSeeds(source):
    files = listdir(source)
    if not isdir('phrase'):
        try:
            mkdir('phrase')
        except OSError:
            print('Creation of text-to-speech output drectory \'phrase\' failed')
            exit(1)
    if not isdir('word'):
        try:
            mkdir('word')
        except OSError:
            print('Creation of text-to-speech output drectory \'word\' failed')
            exit(1)
    for filename in files: 
        if filename.endswith('json'):
            with open(join(source,filename)) as json_file:
                data = json.load(json_file)
                phrase_seeds = processPhrases(data["phrases"].values())
                words_seeds = processPhrases(data["words"].values()) 
                for i in phrase_seeds:
                    generators.generate_phrase_tts(i, join(source, 'phrase'))
                with open('seed_guide.txt', 'w+') as guide:
                    for i in words_seeds:
                        guide.write(i + '\n')
                        generators.generate_words_tts(i, join(source, 'word'))