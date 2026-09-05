from typing import Any, Self, Type

from pydantic import BaseModel, model_validator

from pydantic_parse.argparse_model.field import ArgFieldInfo
from pydantic_parse.argparse_model.internal_attr import InternalAttr
from pydantic_parse.argparse_model.meta import ArgModelMeta


class ArgModel(BaseModel, metaclass=ArgModelMeta):
    """
    Argument model.

    Defines a set of arguments, their type and description.
    """

    def arg_dump(self, **kwargs) -> dict[str, Any]:
        """
        Argument dump.

        Model dump of arguments present in ArgModel instance.
        Exclude internal attributes (non-arguments)

        Arguments can be further excluded via exclude={name: True} in **kwargs.
        Internal arguments however are always excluded.
        User standard model_dump()
        """
        exclude_args = {key: True for key in InternalAttr}

        if not "exclude" in kwargs:
            kwargs["exclude"] = {}

        kwargs["exclude"] |= exclude_args

        return self.model_dump(**kwargs)

    # @classmethod
    # def subparser(cls) -> str:
    #     """
    #     Subparser.

    #     Default value of internal field is set at child class definition.
    #     """
    #     ret = cls.model_fields[InternalAttr.subparser].default
    #     return ret

    # TODO: property like model_fields
    @classmethod
    def arg_fields(cls) -> dict[str, ArgFieldInfo]:
        """
        Model info that represent arguments.

        Non-argument (internal) attribuges are skipped.
        """
        ret = {
            field_name: field_info
            for field_name, field_info in cls.model_fields.items()
            if not field_name in InternalAttr
        }

        return ret

    # @model_validator(mode="before")
    # def check_hidden(self) -> Self:
    #     # TODO: check that hidden fields have not been given in input; raise error that they are reserved
    #     # raise ValueError("Provide subparser in your ArgModel class definition!")
    #     return self

    @model_validator(mode="before")
    def check_field_info(self) -> Self:
        # TODO: mode-before model validator that all fields have a description and annotation
        return self
