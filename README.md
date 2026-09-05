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
        name: TestChoices = ArgField(description="Name")
        some_value: Optional[str] = ArgField(
            description="value",
            optional=True,
            default=None,
            flag=True
        )
        flag: bool = ArgField(description="flag", default=False, flag=True)

    parser = PydanticArgParser()
    parser.add_arguments_from_model(TestModel)
    args = parser.parse_args()
```

CLI result:
```bash
$ pydantic-parse -h
usage: pydantic-parse [-h] [--some-value SOME_VALUE] [--flag] {Alice,Bob}

positional arguments:
  {Alice,Bob}           Name

options:
  -h, --help            show this help message and exit
  --some-value SOME_VALUE
                        value
  --flag                flag
```  

CLI input:

```bash
my-package Alice --some-value 42
```

results in `vars(args)`:

```python
{
  'name': <TestChoices.alice: 'Alice'>,
  'some_value': '42',
  'flag': False
}
```

Or of course
```python
model = TestModel(**vars(args))
```

gives
```python
TestModel
name=<TestChoices.alice: 'Alice'> some_value='42' flag=False
```

-----
*Made with [poetiq](https://pypi.org/project/poetiq)*
