import enum
from pathlib import Path
from typing import Any, Union, get_args, get_origin

from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from pydantic_parse.exceptions import PydanticParseValueError

# from pydantic.fields import _FieldInfoInputs,  _FieldInfoAsDict


class ArgFieldInfo(FieldInfo):  # type: ignore[misc]
    __slots__ = ("flag", "optional", "informative", "const", "cli")

    def __init__(
        self,
        flag: bool,
        optional: bool,
        informative: bool,
        const: Any,
        cli: bool,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.flag: bool = flag
        self.optional: bool = optional
        self.informative: bool = informative
        self.const: Any = const
        self.cli: bool = cli

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
        if self.annotation is Path:
            return str
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
        new.cli = cli
        return new


def ArgField(
    *,
    flag: bool = False,
    optional: bool = False,
    informative: bool = False,
    const: Any = None,
    cli: bool = True,
    **kwargs: Any,
) -> Any:
    field_info = Field(**kwargs)
    return ArgFieldInfo.from_field_info(
        field_info,
        flag=flag,
        optional=optional,
        informative=informative,
        const=const,
        cli=cli,
    )
