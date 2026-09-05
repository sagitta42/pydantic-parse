import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
import pytest
import sys
import os

from dotenv import dotenv_values

from pydantic_parse.argmodel.field import ArgField
from pydantic_parse.argmodel.model import ArgModel

env_config = dotenv_values()
is_debug = env_config.get("DEBUG", "").lower() in ("true", "1")
test_eann = env_config.get("TEST_EANN", "").lower() in ("true", "1")

if is_debug:
    path_current = os.path.dirname(__file__)
    # make src modules accessible in all test_* files without having to install the package
    path_to_src = os.path.join(path_current, "..", "src")
    path_to_src_absolute = os.path.abspath(path_to_src)
    sys.path.insert(0, path_to_src_absolute)

PATH_TO_ASSETS = Path(os.path.dirname(__file__))
PATH_TO_CONFIGS = PATH_TO_ASSETS / "configs"


class TestCaseModel(ArgModel):
    name: str = ArgField(description="Name")
    value: Optional[str] = ArgField(
        description="value", optional=True, default=None, informative=True, const="foo"
    )
    flag: bool = ArgField(description="flag", default=False, flag=True)


def read_test_config(filename: str) -> TestCaseModel:
    config_path = PATH_TO_CONFIGS / f"{filename}.json"
    with open(config_path) as f:
        dataset_info = TestCaseModel(**json.load(f))
    return dataset_info


def get_test_case(filename) -> TestCaseModel:
    test_case = read_test_config(filename)
    ret = [pytest.param(test_case, id=filename)]
    return ret


@pytest.fixture(params=get_test_case("test_case"))
def test_case_model(request) -> TestCaseModel:
    return request.param
