import json
from typing import Optional
from pydantic import Field

from pydantic_parse.argparse.argument_parser import PydanticArgParser
from pydantic_parse.argparse_model.field import ArgField, ArgFieldInfo
from pydantic_parse.argparse_model.model import ArgModel
from pydantic_parse.exceptions import PydanticParseTypeError
from pydantic_parse.logger import logg

from tests.conftest import PATH_TO_CONFIGS, TestCaseModel

filename = "test_model"
model_config_path = PATH_TO_CONFIGS / f"{filename}.json"


def test_bad_model():
    try:

        class BadArgModel(ArgModel):
            name: str = ArgField(description="Name")
            value: Optional[str] = ArgField(
                description="value",
                optional=True,
                default=None,
                informative=True,
                const="foo",
            )
            flag: bool = Field(description="flag", default=False)  # not allowed

    except PydanticParseTypeError as e:
        logg.debug(e)


def test_arg_field():
    arg_info = TestCaseModel.arg_fields()["value"]
    dct = arg_info.as_dict()

    logg.debug("Serialized")
    logg.debug(dct)

    rev_info = ArgFieldInfo(**dct)
    logg.debug("Re-Serialized")
    logg.debug(rev_info)


def test_args(test_case_model):
    logg.debug(test_case_model.model_dump())
    logg.debug(test_case_model.arg_dump())


# def test_add_argument(test_case_model):
#     parser = PydanticArgParser()
#     parser.add_argument_from_model("value", test_case_model)
#     args = parser.parse_args()

#     logg.debug(args)
