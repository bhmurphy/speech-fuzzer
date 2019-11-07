import pyttsx3
from os.path import join
from re import sub

# @TODO: Convert files to wav because apparently they aren't actually saved
# as wav files?
def generate_words_tts(phrase, save_dir: str):
    """Generate audio files for individual words using text to speech
    system

    Args:
        phrase: Phrase to be translated into audio files. Should be
            either a string or a list
        save_dir: Directory to save generated files to
    """
    # Initialize text to speech system
    engine = pyttsx3.init()

    # If input was a string, convert it to a list
    if isinstance(phrase, str):
        phrase = phrase.split()

    # Append the first word of the phrase to the end of the phrase.
    # This is 100% because of a bug in pyttsx3 (or potentially in
    # Apple's text-to-speech). If you don't do this for some weird
    # reason, the first word processed will result in an invalid
    # file. If you try to run play on it, you get:
    # play FAIL formats: can't open input file `file.wav': Missing SSND chunk in AIFF file
    phrase.append(phrase[0])

    for word in phrase:
        filename = join(save_dir, word + '.wav')
        engine.save_to_file(word, filename)
    engine.runAndWait()

def generate_phrase_tts(phrase, save_dir):
    """Save entire phrase to file. Useful for generating a whole
    phrase when you do not want to piece together separate words

    Args:
        phrase: Phrase to be translated into an audio file
        save_dir: Directory to save generated file to
    """
    # Initialize text to speech system
    engine = pyttsx3.init()
    remove_whitespace = sub('\s+', '_', phrase)
    filename = join(save_dir, remove_whitespace + '.wav')
    engine.save_to_file(phrase, filename)
    engine.runAndWait()

if __name__ == "__main__":
    generate_phrase_tts('wow what a cool future', 'test')