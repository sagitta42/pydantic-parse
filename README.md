# pydantic-parse


## Usage


Import:
```bash
>>> from pydantic_parse import is_answer
>>> is_answer(42)
True
>>> is_answer(43)
False
```

CLI:
```bash
$ pydantic-parse -h
usage: pydantic-parse [-h] {foo} ...

positional arguments:
  {foo}
    foo       foo functionalities

options:
  -h, --help  show this help message and exit

$ pydantic-parse foo -h
usage: pydantic-parse foo [-h] answer

positional arguments:
  answer      Answer to check

options:
  -h, --help  show this help message and exit
```

Example:
```bash
$ pydantic-parse foo 67
Is 67 the answer to the question of life, universe, and everything? - False
```

Equivalent to `python -m pydantic_parse foo 67`


## For dummies / development notes

Local install

```bash
pip install /path/to/pydantic-parse
```

Run tests
```bash
cd /path/to/pydantic-parse
source venv/bin/activate
```

Option 1: run `poetry install` to install this package into its own `venv`

Option 2: set up debug environment `cp .env.template` to make source files visible to `pytest`.

Then, run `pytest`.

Note: `poetiq` has already fully set up `venv` for you, including installing `pytest`.

Add remote
```bash
git remote add origin https://...
```


-----
*Made with [poetiq](https://pypi.org/project/poetiq)*
