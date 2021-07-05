# TextChunkGenerator
This script shall make the translation of chunks of texts easier by dividing a large text into smaller chunks while preserving longer dialogues.
The length of the smaller chunks is given by the number of words that shall be contained in these text-chunks.
The number of words is a minimum value, so all chunks of text consist of at least this amount of words.

Currently the text chunk generator tries to preserve dialogues.
I.e., `"Hello! World! My name is Test!"` is going to be one sentence.
Also: `"Hello! World! My name is Test!" said Test.` is going to be one sentence.

If the script is run with the `-p` parameter, multiple direct-speech-containing sentences in sequence are guaranteed to be within one generated chunk of text.

Direct speech is only recognized with the "-quotation marks!

## Installation
- create virtual environment with *virtualenv*
    - `python3 -m virtualenv env`
- activate virtual environment
    - `source env/bin/activate`
- download required packages
    - `pip3 -r requirements.txt`
- download nltk extra data
    - `python3 -m nltk.downloader punkt -d .`

## Usage
```
A program to divide piped in text into chunks of text based on number of words while still preservering sentences. The result is written to an ouput file.
Note: This program does not properly handles unicode chars.
       [-h] [-f FILE] [-i WORD_NUM] [-d DELIMITER] [-o OUTPUT] [-p]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Instead of using pipes to input text, specify a file that should be used to split the text into chunks.
  -i WORD_NUM, --word_num WORD_NUM
                        Specifies the number of words that shall be used to divide the text into.
  -d DELIMITER, --delimiter DELIMITER
                        Specifies the delimiter that is used to concatenate the splitted texts.
  -o OUTPUT, --output OUTPUT
                        Sets the filename of the output. By default it is piped to stdout.
  -p, --preserve        Flag that indicates if all dialogues shall be preserved.
```
