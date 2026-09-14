# pydantic-parse

Pydantic adaptor for argparse

Example
```python

from pydantic_parse import ArgField, ArgModel, PydanticArgParser

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
        bool_flag: bool = ArgField(description="flag", default=False, flag=True)
        folder: Path = ArgField(description="Folder", flag=True, alias="folder_path")

    parser = PydanticArgParser()
    parser.add_arguments_from_model(TestModel)
    args = parser.parse_args()
```

CLI result:
```bash
$ my-package -h
usage: my-package [-h] [--optional-flag OPTIONAL_FLAG] [--bool-flag] --folder-path FOLDER_PATH {Alice,Bob}

positional arguments:
  {Alice,Bob}           Arg with choices

options:
  -h, --help            show this help message and exit
  --optional-flag OPTIONAL_FLAG
                        Optional flag
  --bool-flag           Bool flag
  --folder-path FOLDER_PATH
                        Folder arg
```

CLI input:

```bash
$ my-package --optional-flag foo --folder tests/ Alice
```

results in `vars(args)`:

```python
{
    'choice_arg': <TestChoices.alice: 'Alice'>,
    'optional_flag': 'foo',
    'bool_flag': False,
    'folder_path': PosixPath('tests')
}
```

And
```python
model = TestModel(**vars(args))
```

gives
```python
TestModel
ignored_arg='foo' choice_arg=<TestChoices.alice: 'Alice'> optional_flag='foo' bool_flag=False folder=PosixPath('tests')
```

-----
*Made with [poetiq](https://pypi.org/project/poetiq)*
