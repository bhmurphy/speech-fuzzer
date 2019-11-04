# speech-fuzzer

Final project for CS 6501: Analysis of Software Artifacts

Basically a scratchpad at the moment.

## Random notes:

pyttsx3 -> Text to speech
pysox (sox) -> Complex audio manipuation (pitch shift, add noise)
pydub -> easier audio manipulation


## Related work:
LipFuzzer (for security)
https://scholar.google.com/scholar?q=foreign+accent+speech+synthesis&hl=en

run google assistant:
googlesamples-assistant-pushtotalk --device-model-id fuzzing-personal-assistants-hunters-macbook --project-id fuzzing-personal-assistants -v

OR:

cd to virtualenv folder containing the pushtotalk.py file and run
python pushtotalk.py -v