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
    def __init__(
        self,
        prog: str | None = None,
        usage: str | None = None,
        description: str | None = None,
        epilog: str | None = None,
        parents: Iterable[argparse.ArgumentParser] = [],
        formatter_class: _FormatterClass | None = None,
        prefix_chars: str = "-",
        fromfile_prefix_chars: str | None = None,
        argument_default: Any = None,
        conflict_handler: str = "error",
        add_help: bool = True,
        allow_abbrev: bool = True,
        exit_on_error: bool = True,
    ) -> None:
        super().__init__(
            prog=prog,
            usage=usage,
            description=description,
            epilog=epilog,
            parents=parents,
            formatter_class=formatter_class or CompactHelpFormatter,
            prefix_chars=prefix_chars,
            fromfile_prefix_chars=fromfile_prefix_chars,
            argument_default=argument_default,
            conflict_handler=conflict_handler,
            add_help=add_help,
            allow_abbrev=allow_abbrev,
            exit_on_error=exit_on_error,
        )

    def add_arguments_from_model(
        self,
        model: Type[ArgModel],
        choices: dict[str, list[Any]] = {},
        kwargs: dict[str, dict] = {},
    ):
        logg.debug(f"Adding arguments from model: {model.__name__}")
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

        logg.debug(f"{arg_name} - {arg_info.arg_type}")
        return self.add_argument(
            *arg_name_options,
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
