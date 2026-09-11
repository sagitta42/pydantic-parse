import argparse
from typing import Any, Type

from pydantic_parse.argmodel.field import ArgFieldInfo
from pydantic_parse.argmodel.model import ArgModel

from pydantic_parse.logger import logg


class PydanticArgParser(argparse.ArgumentParser):
    def add_arguments_from_model(
        self,
        model: Type[ArgModel],
        choices: dict[str, list[Any]] = {},
        kwargs: dict[str, dict] = {},
    ):
        for arg_name, arg_info in model.arg_fields().items():
            if arg_info.cli:
                self.add_argument_from_field(
                    arg_name,
                    arg_info,
                    choices=choices.get(arg_name, None),
                    **kwargs.get(arg_name, {}),
                )

    def add_argument_from_field(
        self,
        name: str,
        arg_info: ArgFieldInfo,
        choices: list[Any] | None = None,
        **kwargs,
    ) -> argparse.Action:
        arg_name = arg_info.alias or name
        if arg_info.flag:
            arg_name = arg_name.replace("_", "-")
            arg_name = f"--{arg_name}"

        # TODO: flag must always have default False? (store_true concept)
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
        flag_kwargs = {}
        if arg_info.flag:
            flag_kwargs["required"] = not arg_info.optional

        return super().add_argument(
            arg_name,
            type=arg_info.arg_type,
            choices=choices or arg_info.choices,
            default=arg_info.arg_default if arg_info.optional else None,
            nargs=(
                "?"
                if (arg_info.flag and arg_info.informative)
                or (not arg_info.flag and arg_info.optional)
                else None
            ),
            const=arg_info.const if arg_info.flag and arg_info.informative else None,
            help=arg_info.description,
            **flag_kwargs,
            **kwargs,
        )
