from pydantic_parse.foo import is_answer
from pydantic_parse.logger import logg

from tests.conftest import PATH_TO_CONFIGS

def test_foo():
    input = 42
    output = is_answer(input)
    assert output, f"Test failed because {input} is not the answer"


def test_example(test_case_example):
    input = test_case_example.answer
    output = is_answer(input)
    assert output, f"Test failed because {input} is not the answer"
