import argparse
import sys

from pydantic_parse.foo import is_answer
from pydantic_parse.logger import logg

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    foo_subparser = subparsers.add_parser(
        "foo", help="foo functionalities"
    )
    foo_subparser.add_argument("answer", type=int, help="Answer to check")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    output = is_answer(args.answer)
    logg.info(f"Is {args.answer} the answer to the question of life, universe, and everything? - {output}")

if __name__ == "__main__":
    main()
