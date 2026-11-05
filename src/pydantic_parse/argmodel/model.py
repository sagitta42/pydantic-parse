from typing import Any, Self, Type

from pydantic import BaseModel, model_validator

from pydantic_parse.argmodel.field import ArgFieldInfo
from pydantic_parse.argmodel.internal_attr import InternalAttr
from pydantic_parse.argmodel.meta import ArgModelMeta


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
        Model fields that represent arguments.

        Non-argument (internal) attribuges are skipped.
        """
        ret = {
            field_name: field_info
            for field_name, field_info in cls.model_fields.items()
            if not field_name in InternalAttr
        }

        return ret

    @classmethod
    def cli_fields(cls) -> dict[str, ArgFieldInfo]:
        """
        Model fields that represent CLI arguments.

        Non-CLI arguments are skipped.
        """
        ret = {
            field_name: field_info
            for field_name, field_info in cls.arg_fields().items()
            if field_info.cli
        }
        return ret

    @classmethod
    def get_arg_params(cls, arg: str, exclude: str | list[str] = []) -> dict[str, Any]:
        """
        Get parameters of given ArgField.

        Args:
            exclude (str | list[str]): properties to exclude

        To be used for convenience when defining ArgField in child ArgModel
            to inherit field parameters of choice from parent ArgField.

        Example:

            class BaseArgModel(ArgModel):
                param: str = ArgField(description="Parameter") # not optional
                flag: Optional[str] = ArgField(
                    description="Flag",
                    informative=True, # assigned "bar" if do --flag with no input; not providing --flag at all defaults to None
                    const="bar", 
                )

            class MyArgModel(BaseArgModel):
                param: str = ArgField(default="foo", optional=True, **BaseArgModel.get_arg_params("param", exclude=["default", "optional"])) # is optional, inherits description
                flag: Optional[str] = ArgField(
                    **BaseArgModel.get_arg_params(
                        "flag", exclude=["const", "informative"]
                    ), # is not informative, not used as bare --flag with nothing provided
                )

        TODO: #3 automatize in ArgField e.g. inherit=True means inheriting all non-defined parameters from parent

                
        Annotation is always excluded as it cannot be provided as kwarg to Field()
            (Deprecated in Pydantic V2.0 to be removed in V3.0)
        """
        arg_info = cls.arg_fields()[arg]
        to_exclude = exclude if isinstance(exclude, list) else [exclude]
        if "annotation" not in to_exclude:
            to_exclude.append("annotation")

        ret = arg_info.as_dict(exclude=to_exclude)
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
