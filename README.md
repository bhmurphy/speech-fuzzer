# speech-fuzzer

Final project for CS 6501: Analysis of Software Artifacts   

## Installing Dependencies

### Python Dependencies

We recommend making a new [virtual environment](https://docs.python.org/3/tutorial/venv.html) for Speech Fuzzer's python dependencies. To install Speech Fuzzer's python dependencies, use pip:  

`pip install -r requirements.txt`

### Other Dependencies

Speech Fuzzer also relies on both ffmpeg and sox. To install on Ubuntu:  

```
apt-get install ffmpeg
apt-get install sox
```

To install on MacOS with [Homebrew](https://brew.sh/):

```
brew install ffmpeg
brew install sox
```

## Running the fuzzer:

Basic usage for speech fuzzer looks like the following:  

`python speech-fuzzer.py [OPTIONS]`

### Options

Below are the possible options for Speech Fuzzer:

```
-h, --help                                           show this help message and exit
-s SOURCE, --source SOURCE                           Path to the source directory where seeds
                                                     are stored
-o OUTPUT, --output OUTPUT                           Path to the output directory where results
                                                     will be stored
-n NUM, --num NUM                                    The number of iterations you want to run
                                                     for each type. Default = 5
-i {text,word,phrase}, --ignore {text,word,phrase}   The type of seeds you want to ignore
-t {text,word,phrase}, --type {text,word,phrase}     The one type of seed you want to use
```

We give more detailed explanations of each option in the sections below.

#### Source

The directory that stores the seeds to fuzz. Defaults to `seeds` Speech fuzzer can accept three different types of seed input: phrase audio, text, and word audio. Each type of seed has an expected input format.

* Phrase audio seeds are the simplest. These files should be in wav format, and are generally intended to be phrases that one would say to a personal assistant. For example, a phrase seed might be a wav file that is a recording of a person saying "How does the weather look outside?" Phrase seeds should be stored in `<SOURCE>/phrase`
  Any mutations chosen for a phrase seed are applied to the entire file. For example, if a pitch shift mutation is chosen for a phrase seed during the fuzzing process, the entire file will be pitch-shifted.
* Word audio seeds should also be in a wav format, and should be recordings of single words that can be pieced together to make a phrase. Each word file has the chance to be mutated separately. For example, the mutation may consist of pitch shifting only one word in the given phrase, instead of the entire generated recording.
 Word audio seeds require at least one helper JSON file that contains the phrases which should be constructed from the given audio files. The JSON file(s) should contain a dictionary with a single key, "words". The value for this key will be another dictionary consisting of key, value pairs. In these pairs, the values will be the phrases to fuzz. Word seeds and helper JSON files should be stored in `<SOURCE>/words`.
 Synonyms can be included by making a sub-list within the phrase list; the phrase will be generated using all variants of the synonyms provided. For example, if the given phrase is `['is it', ['sunny', 'rainy'], 'outside']`, both the phrase 'is it sunny outside' and the phrase 'is it rainy outside' will be generated. It is important to note, that we expect the word recordings to be named after what the contain. Using the previous example, we would expect the following wav files: `is.wav, it.wav, sunny.wav, rainy.wav, and outside.wav.`  
* Text seeds contain text that will be converted into audio files using the system's text-to-speech platform. These text files should be JSON, and contain a dictionary with two keys: "phrases" and "words". Phrases will be fuzzed like phrase audio, and words will be fuzzed like word audio. Each key contains its own dictionary of key, phrase pairs. The phrase in each of these pairs should be a list containing one or multiple strings that make up the phrase to be fuzzed. Just as for word seeds, synonyms can be substituted in the JSON file. These JSON text seeds should be stored in `<SOURCE>/text`.

**An example seeds folder is included (example-seeds) for reference.**

#### Output

The name of the results directory. Defaults to `results`. After the fuzzer is run, the results folder will contain three items:

* a `failed` folder. This contains all audio samples that failed the client's evaluation criteria.
* a `passed` folder. This contains all audio samples that passed the client's evaluation criteria.
* a text file, named `run_log-YYYY-MM-DD HH:mm:ss.txt`, that contains a report of the fuzzing results. Specifically, it lists how many mutants failed, which mutations caused the failures, and gives a detailed report of the parameters for each failed mutation.

#### Num

The number of iterations to run the fuzzer for. One iteration is defined as mutating every example in the seed set at least once.

#### Ignore

Ignore an input type. For example, running `python speech-fuzzer.py -i word` will ignore all word seeds, but still run phrase and text seeds. This option cannot be used along with the type option.

#### Type

Run fuzzing for a specific input type. For example, running `python speech-fuzzer.py -t word` will only run the fuzzer on the word seeds in the source folder. This option cannot be used along with the ignore option.
