import json
from os import listdir
from os.path import join,abspath
import generators
source = "seeds/text"
for filename in listdir(source): 
    print(filename)
    if filename.endswith('json'):
        with open(join(source,filename)) as json_file:
            data = json.load(json_file)
            print(data)
            strings = []
            for phrase in data["phrases"].values():
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
            print(strings)
            for i in strings:
                generators.generate_phrase_tts(i, source)
