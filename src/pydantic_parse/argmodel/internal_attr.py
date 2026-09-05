import enum


class InternalAttr(enum.StrEnum):
    subparser = "subparser__"

    @classmethod
    def values(cls) -> list[str]:
        return [c.value for c in cls]


class AttrDescription(enum.StrEnum):
    subparser = "Subparser"

    @classmethod
    def from_attr(cls, attr: InternalAttr) -> str:
        return cls[attr.name].value
