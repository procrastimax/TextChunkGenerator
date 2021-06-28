import sys
import argparse
import nltk
from typing import List


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
    return text


def divide_into_chunks(text: str, word_limit: int = 50, delimiter: str = "\n") -> str:
    tokens_sent = nltk.sent_tokenize(text)

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
        default="\n",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Sets the filename of the output. By default it is piped to stdout.",
        default="",
    )
    args = parser.parse_args()

    word_num: int = args.word_num
    delimiter: str = args.delimiter
    text_in: str = ""

    if len(args.file) != 0:
        text_in = parse_from_file(args.file)
    else:
        text_in = parse_from_stdin()

    out_text = divide_into_chunks(
        text=text_in, word_limit=word_num, delimiter=delimiter
    )
    if len(args.output) == 0:
        print(out_text, file=sys.stdout)
    else:
        with open(args.output, "w+") as f:
            f.write(out_text)
            return


if __name__ == "__main__":
    main()
