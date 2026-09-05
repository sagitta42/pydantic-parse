import argparse
import enum
import sys
from typing import Optional

from pydantic_parse.argparse.argument_parser import PydanticArgParser
from pydantic_parse.argparse_model.field import ArgField
from pydantic_parse.argparse_model.model import ArgModel
from pydantic_parse.foo import is_answer
from pydantic_parse.logger import logg


def main():

    class TestChoices(enum.StrEnum):
        a = "a"
        b = "b"

    class TestModel(ArgModel):
        name: TestChoices = ArgField(description="Name")
        some_value: Optional[str] = ArgField(
            description="value",
            optional=True,
            default=None,
        )
        flag: bool = ArgField(description="flag", default=False, flag=True)

    parser = PydanticArgParser()

    parser.add_arguments_from_model(TestModel)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # subparsers = parser.add_subparsers(dest="command")
    # foo_subparser = subparsers.add_parser("foo", help="foo functionalities")
    # foo_subparser.add_argument("answer", type=int, help="Answer to check")

    # output = is_answer(args.answer)
    logg.info(args)


if __name__ == "__main__":
    main()
