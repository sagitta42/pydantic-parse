from typing import Any, Type

from pydantic import BaseModel, Field

from pydantic_parse.argparse_model.field import ArgField, ArgFieldInfo
from pydantic_parse.argparse_model.internal_attr import AttrDescription, InternalAttr
from pydantic_parse.exceptions import PydanticParseTypeError


def nested_merge(first: dict, second: dict) -> dict:
    for key, b_val in second.items():
        if key in first and isinstance(first[key], dict) and isinstance(b_val, dict):
            nested_merge(first[key], b_val)
        else:
            first[key] = b_val
    return first


class ArgModelMeta(type(BaseModel)):
    """
    Metaclass for ArgModel creation.

    Takes care of fields hidden to user.
    Requires model fields to be defined via ArgField rather than standard Field.
    """

    def __new__(
        mcs,
        name: str,
        bases: tuple[Type, ...],
        namespace: dict[str, Any],
        /,
        # subparser: str | None = None,
        **kwds: Any,
    ):
        namespace.setdefault("__annotations__", {})

        # mcs._add_field_namespace_info(namespace, InternalAttr.subparser, subparser)

        cls = super().__new__(mcs, name, bases, namespace, **kwds)

        for field_name, field_info in getattr(cls, "__pydantic_fields__", {}).items():
            if field_name in InternalAttr.values():
                continue

            if not isinstance(field_info, ArgFieldInfo):
                raise PydanticParseTypeError(
                    f"{cls.__name__}.{field_name} must be declared with {ArgField.__name__}(...), "
                    f"not Field() or a bare default (got {type(field_info).__name__})"
                )
        return cls

    @classmethod
    def _add_field_namespace_info(
        mcs, namespace: dict, field_name: InternalAttr, parameter: Any
    ):
        nested_merge(namespace, mcs._get_field_namespace_info(field_name, parameter))

    @classmethod
    def _get_field_namespace_info(
        mcs, field_name: InternalAttr, parameter: Any
    ) -> dict:
        """
        Create information to add to namespace to create field.

        parameter: parameter to be added - defines annotation and default value.
        name: field name

        The default value is crucial to set fixed argument model parameters once during
            child class definition.
        """
        ret = {
            "__annotations__": {field_name: type(parameter)},
            field_name: Field(
                default=parameter, description=AttrDescription.from_attr(field_name)
            ),
        }
        return ret
