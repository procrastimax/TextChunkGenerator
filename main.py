import sys
import argparse
import nltk
import re
from typing import List, Dict, Tuple

# a regex to mark sentences as direct speech sentences
# this regex only matches with sentences that start with a quotation mark and end with a quotation mark
re_compl_direct_speech = re.compile('^".+"$')

# a regex to mark sentences as direct speech sentences
# this regex matches all sentences that contain two quotation marks
re_part_direct_speech = re.compile('".+"')


def parse_from_stdin() -> str:
    text: str = ""
    for line in sys.stdin:
        text += line

    text = clean_text(text)
    return text


def parse_from_file(filename: str) -> str:
    with open(filename, "r") as f:
        file_text = f.read()
        file_text = clean_text(file_text)
        return file_text


def clean_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = text.replace("  ", " ")
    text = text.strip()
    return text


def fix_direct_speech_sentences(sentence_list: List[str]):
    """
    This function fixes edge cases when handling direct speeches.
    I.e., when a line of dialogue is recognized as a single sentence, but the sentence after this starts with a lowercase letter, we want to merge
    these two sentences into one: "'Hello!' said Mrs. Person."

    Also fix the case that multiple sentence within one direct speech does not get splitted.
    I.e., "Hello! World!"

    """
    for i, sentence in enumerate(sentence_list):
        if len(sentence) == 0:
            continue

        # concatenate direct speech sentence with other direct speech sentences
        # find a sentence that starts with " but is not a complete direct speech sentence
        if sentence.startswith('"') and not re_compl_direct_speech.match(sentence):
            j: int = i + 1
            # iterate over all sentences to find the closing quotation mark
            while j < len(sentence_list):
                # if a sentence contains a quotation mark and is also not a complete direct speech sentence
                # then this sentence is probably the closing sentence
                if '"' in sentence_list[j] and not re_compl_direct_speech.match(
                    sentence
                ):
                    # merge all sentence we found so far
                    for a in range(i + 1, j + 1):
                        sentence_list[i] += " " + sentence_list[a]
                        sentence_list[a] = ""
                    break
                j += 1

    # clean out all empty list entries
    # list copy not clean, but functional ;)
    cpy_list = sentence_list.copy()
    sentence_list.clear()
    sentence_list = list(filter(lambda sentence: len(sentence) > 0, cpy_list))

    # concatenate direct speech sentences with following subclauses
    for i, sentence in enumerate(sentence_list):
        if re_compl_direct_speech.match(sentence) and i < len(sentence_list) - 2:
            if len(sentence_list[i + 1]) == 0:
                continue
            if sentence_list[i + 1][0].islower():
                sentence_list[i] += " " + sentence_list[i + 1]
                sentence_list[i + 1] = ""

    return list(filter(lambda sentence: len(sentence) > 0, sentence_list))


def preserve_dialogues(sentence_list: List[str]):
    """
    This function tries to preserve dialogues when parsing sentences.
    This is done by merging all sentences that contain direct speech into one sentence.
    This should prevent the splitting of these dialogues in the later steps.
    """

    direct_speech_tag_list: List[Tuple[str, bool]] = list()
    sentence_list_new: List[str] = []

    # mark sentences that contain direct speech
    for sentence in sentence_list:
        if re_part_direct_speech.match(sentence):
            direct_speech_tag_list.append((sentence, True))
        else:
            direct_speech_tag_list.append((sentence, False))

    # merge all neighboring direct speech sentences into one block
    for i, tag_tuple in enumerate(direct_speech_tag_list):
        if len(tag_tuple[0]) == 0:
            continue
        if tag_tuple[1] == False:
            sentence_list_new.append(tag_tuple[0])
        else:
            sentence: str = ""
            j: int = i + 1

            # find last direct speech containing sentence
            while j < len(direct_speech_tag_list):
                if direct_speech_tag_list[j][1] == False:
                    break
                else:
                    j += 1

            # append all sentences until last direct speech containing sentence
            for a in range(i, j):
                sentence += " " + direct_speech_tag_list[a][0]
                direct_speech_tag_list[a] = ("", False)
            sentence_list_new.append(sentence)

    for i, s in enumerate(sentence_list_new):
        sentence_list_new[i] = s.strip()

    return sentence_list_new


def divide_into_chunks(text: str, word_limit: int = 50, delimiter: str = "\n\n", is_preserving_dialogues : bool = False) -> str:
    tokens_sent = nltk.sent_tokenize(text)

    # fix uncorrect dialog sentences
    tokens_sent = fix_direct_speech_sentences(tokens_sent)

    if is_preserving_dialogues:
        tokens_sent = preserve_dialogues(tokens_sent)

    output_text: List[str] = []
    word_counter = 0

    is_init = True

    for sentence in tokens_sent:

        # slow af, but works
        word_tokens = nltk.word_tokenize(sentence)
        word_tokens = [word for word in word_tokens if word.isalpha()]
        word_counter += len(word_tokens)

        if is_init:
            output_text.append(sentence)
            is_init = False
            continue

        if word_counter >= word_limit:
            word_counter = 0
            output_text.append(sentence)
        else:
            # add new sentence to last sentence
            output_text[-1] += " " + sentence

    return delimiter.join(output_text)


def main():
    parser = argparse.ArgumentParser(
        "A program to divide piped in text into chunks of text based on number of words while still preservering sentences. The result is written to an ouput file.\nNote: This program does not properly handles unicode chars."
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Instead of using pipes to input text, specify a file that should be used to split the text into chunks.",
        default="",
    )
    parser.add_argument(
        "-i",
        "--word_num",
        type=int,
        help="Specifies the number of words that shall be used to divide the text into.",
        default=50,
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        type=str,
        help="Specifies the delimiter that is used to concatenate the splitted texts.",
        default="\n\n",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Sets the filename of the output. By default it is piped to stdout.",
        default="",
    )
    parser.add_argument(
        "-p",
        "--preserve",
        action="store_true",
        help="Flag that indicates if all dialogues shall be preserved."
    )
    args = parser.parse_args()

    word_num: int = args.word_num
    delimiter: str = args.delimiter
    text_in: str = ""
    is_preserving_dialogue : bool = args.preserve

    if len(args.file) != 0:
        text_in = parse_from_file(args.file)
    else:
        text_in = parse_from_stdin()

    out_text = divide_into_chunks(
        text=text_in, word_limit=word_num, delimiter=delimiter, is_preserving_dialogues=is_preserving_dialogue
    )
    if len(args.output) == 0:
        print(out_text, file=sys.stdout)
        pass
    else:
        with open(args.output, "w+") as f:
            f.write(out_text)
            return


if __name__ == "__main__":
    main()
