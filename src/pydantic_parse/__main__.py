import enum
from pathlib import Path
import sys
from typing import Literal, Optional

from pydantic_parse.argparse.argument_parser import PydanticArgParser
from pydantic_parse.argmodel.field import ArgField
from pydantic_parse.argmodel.model import ArgModel
from pydantic_parse.logger import logg


def main():

    class TestChoices(enum.StrEnum):
        alice = "Alice"
        bob = "Bob"

    class TestModel(ArgModel):
        ignored_arg: str = ArgField(
            default="foo",
            description="Ignored argument (will not be added to CLI)",
            cli=False,
        )
        choice_arg: TestChoices = ArgField(description="Arg with choices")
        optional_flag: Optional[str] = ArgField(
            description="value", optional=True, default=None, flag=True
        )
        # TODO: informative flag
        # TODO: handle bool flag default should always be False (action store_true)
        bool_flag: bool = ArgField(description="flag", default=False, flag=True)
        folder: Path = ArgField(description="Folder", flag=True)

    parser = PydanticArgParser()

    parser.add_arguments_from_model(TestModel)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # subparsers = parser.add_subparsers(dest="command")
    # foo_subparser = subparsers.add_parser("foo", help="foo functionalities")
    # foo_subparser.add_argument("answer", type=int, help="Answer to check")

    logg.info("Parsed arguments:")
    logg.info(vars(args))

    logg.info("Pydantic model:")
    model = TestModel(**vars(args))
    logg.info(model)


if __name__ == "__main__":
    main()
