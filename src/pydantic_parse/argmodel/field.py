import enum
from typing import Any, Optional, Union, get_args, get_origin

from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from pydantic_parse.exceptions import PydanticParseValueError

# from pydantic.fields import _FieldInfoInputs,  _FieldInfoAsDict


class ArgFieldInfo(FieldInfo):  # type: ignore[misc]
    __slots__ = ("flag", "optional", "informative", "const", "alt", "cli")

    def __init__(
        self,
        flag: bool,
        optional: bool,
        informative: bool,
        const: Any,
        alt: str | list[str],
        cli: bool,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.flag: bool = flag
        self.optional: bool = optional
        self.informative: bool = informative
        self.const: Any = const
        self.alt: str | list[str] = alt
        self.cli: bool = cli

    @property
    def alt_names(self) -> list[str]:
        return self.alt if isinstance(self.alt, list) else [self.alt]

    @property
    def choices(self) -> list | None:
        assert self.arg_type is not None
        if issubclass(self.arg_type, enum.Enum):
            ret = [item.value for item in self.arg_type]
            return ret
        return None

    @property
    def arg_type(self) -> type:
        """
        Get argument type from annotation.

        Extract real type from type union to cover Optional[type] case.
        """
        # TODO: validator
        assert self.annotation is not None
        if get_origin(self.annotation) is Union:
            types = get_args(self.annotation)
            real_types = [tp for tp in types if not tp is type(None)]
            # TODO: validator
            assert len(real_types) == 1
            return real_types[0]
        return self.annotation

    @property
    def arg_default(self) -> Any:
        ret = self.default
        if isinstance(ret, enum.Enum):
            ret = ret.value
        return ret

    def as_dict(self) -> dict[str, Any]:
        """
        Serialize argument properties as dict.

        Get FieldInfo serialization and extract annotation and attributes.
        Add custom argument field info slots.
        Ignore pydantic undefined properties.
        """

        ret = dict(self.asdict())
        ret.pop("metadata")

        attr: dict[str, Any] = ret.pop("attributes")
        slots = {name: getattr(self, name) for name in self.__class__.__slots__}
        full_attr = attr | slots
        defined_attr = {
            name: value
            for name, value in full_attr.items()
            if value is not PydanticUndefined
        }

        ret |= defined_attr

        return ret

    @classmethod
    def from_field_info(
        cls,
        field_info: FieldInfo,
        *,
        flag: bool,
        optional: bool,
        informative: bool,
        const: Any,
        alt: str | list[str],
        cli: bool,
    ) -> "ArgFieldInfo":
        new = cls.__new__(cls)
        for slot in FieldInfo.__slots__:
            setattr(new, slot, getattr(field_info, slot))

        if (optional or not cli) and new.default is PydanticUndefined:
            # TODO: include default_factory
            # if optional and new.is_required():
            arg_descr = "Optional" if optional else "Non-CLI"
            raise PydanticParseValueError(
                f"{arg_descr} ArgField must have a defined default! Please provide default="
            )

        new.flag = flag
        new.optional = optional
        new.informative = informative
        new.const = const
        new.alt = alt
        new.cli = cli
        return new


def ArgField(
    *,
    flag: bool = False,
    optional: bool = False,
    informative: bool = False,
    const: Optional[Any] = None,
    alt: str | list[str] = [],
    cli: bool = True,
    **kwargs: Any,
) -> Any:
    """
    Create an argument field representing argparse.ArgumentParser argument.

    Args:
        flag (bool): field is a flag i.e. will become a optional argument i.e. --name
        optional (bool): field is optional i.e. will become a non-required argument i.e. [name]
        informative (bool): field is informative i.e. has a const value i.e. providing simply --name sets a const value that may differ from default (for flags only)
        const (bool): value to set in argument in case simply --name is provided in CLI (optional)
        alt (str | list[str]): alternative name(s) for flag i.e. providing e.g. -n will result in --name, -n options
        cli (bool): field is CLI argument; if False will be present in pydantic model but ignored by PydanticArgParser (defaults to True)

    """
    field_info = Field(**kwargs)
    return ArgFieldInfo.from_field_info(
        field_info,
        flag=flag,
        optional=optional,
        informative=informative,
        const=const,
        alt=alt,
        cli=cli,
    )
