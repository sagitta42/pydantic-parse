from __future__ import annotations

import argparse
from typing import Any, Iterable, Type

from pydantic_parse.argmodel.field import ArgFieldInfo
from pydantic_parse.argmodel.model import ArgModel

from pydantic_parse.logger import logg

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import _FormatterClass


class CompactHelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action: argparse.Action) -> str:
        """
        Format flag description.

        Instead of:
            -f FLAG, --flag FLAG    Flag description
        Do:
            -f, --flag FLAG         Flag description
        """
        if len(action.option_strings) == 0 or action.nargs == 0:
            return super()._format_action_invocation(action)

        main_arg_name = self._get_default_metavar_for_optional(action)
        arg_input_str = self._format_args(action, main_arg_name)
        ret = ", ".join(action.option_strings) + " " + arg_input_str
        return ret


class PydanticArgParser(argparse.ArgumentParser):
    def __init__(self, formatter_class: _FormatterClass | None = None, **kwargs):
        super().__init__(
            formatter_class=formatter_class or CompactHelpFormatter, **kwargs
        )

    def add_arguments_from_model(
        self,
        model: Type[ArgModel],
        choices: dict[str, list[Any]] = {},
        kwargs: dict[str, dict] = {},
    ):
        logg.debug(f"Adding arguments from model: {model.__name__}")
        for arg_name, arg_info in model.arg_fields().items():
            kwname = arg_info.alias or arg_name
            if arg_info.cli:
                self.add_argument_from_field(
                    arg_name,
                    arg_info,
                    choices=choices.get(arg_name, None),
                    **kwargs.get(kwname, {}),
                )

    def add_argument_from_field(
        self,
        name: str,
        arg_info: ArgFieldInfo,
        choices: list[Any] | None = None,
        **kwargs,
    ) -> argparse.Action:
        logg.debug(f"Adding argument: {name}")

        arg_name = arg_info.alias or name
        if arg_info.flag:
            arg_name = arg_name.replace("_", "-")
            arg_name = f"--{arg_name}"

        arg_name_options = [arg_name] + arg_info.alt_names
        logg.debug(f"Arg name options: {arg_name_options}")

        # TODO: flag must always have default False? (store_true concept)
        if arg_info.flag and arg_info.arg_type is bool:
            return self.add_argument(
                *arg_name_options,
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

        type_kwargs = {}
        if not arg_info.arg_type is Any:
            type_kwargs["type"] = arg_info.arg_type

        logg.debug(f"{arg_name} - {arg_info.arg_type}")
        return self.add_argument(
            *arg_name_options,
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
            **type_kwargs,
            **flag_kwargs,
            **kwargs,
        )
