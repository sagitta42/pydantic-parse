import argparse
from typing import Type

from pydantic_parse.argparse_model.field import ArgFieldInfo
from pydantic_parse.argparse_model.model import ArgModel


class PydanticArgParser(argparse.ArgumentParser):
    def add_arguments_from_model(self, model: Type[ArgModel]):
        for arg_name, arg_info in model.arg_fields().items():
            self.add_argument_from_field(arg_name, arg_info)

    def add_argument_from_field(
        self, name: str, arg_info: ArgFieldInfo, **kwargs
    ) -> argparse.Action:
        arg_name = name.replace("_", "-")
        if arg_info.flag:
            arg_name = f"--{arg_name}"

        if arg_info.flag and arg_info.arg_type is bool:
            return self.add_argument(
                arg_name,
                action="store_true",
                default=False if arg_info.is_required() else arg_info.default,
                help=arg_info.description,
            )

        # FIXME: currently for bool
        # if default was set but is not optional,
        # ends up giving None in default but allows to be not given
        # in theory, no non-optional flags --> unify, currently quickfix
        return super().add_argument(
            arg_name,
            type=arg_info.arg_type,
            choices=arg_info.choices,
            default=arg_info.default if arg_info.optional else None,
            nargs=(
                "?"
                if (arg_info.flag and arg_info.informative)
                or (not arg_info.flag and arg_info.optional)
                else None
            ),
            const=arg_info.const if arg_info.flag and arg_info.informative else None,
            help=arg_info.description,
            **kwargs,
        )
